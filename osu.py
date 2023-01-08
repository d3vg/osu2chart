import copy
from os.path import exists
from configparser import ConfigParser, DuplicateOptionError

class OsuTimingPoint:
    def __init__(self, time, beat_length, meter, sample_set, sample_index, volume, uninherited, effects):
        self.time = time
        self.beat_length = beat_length
        self.meter = meter
        self.sample_set = sample_set
        self.sample_index = sample_index
        self.volume = volume
        self.uninherited = uninherited
        self.effects = effects

    def __str__(self):
        return f"{self.time},{self.beat_length},{self.meter},{self.sample_set},{self.sample_index},{self.volume},{self.uninherited},{self.effects}"

class OsuHitObject:
    def __init__(self, x, time, type, end_time):
        self.x = x
        self.time = time
        self.type = type
        self.end_time = end_time

    def __str__(self):
        return f"{self.x},{self.time},{self.type},{self.end_time}"

class OsuFile:
    def __init__(self):
        self.audio_filename = ""
        self.audio_lead_in = 0
        self.preview_time = 0
        self.mode = 0
        self.special_style = 0

        self.bookmarks = []

        self.title = ""
        self.title_unicode = ""
        self.artist = ""
        self.artist_unicode = ""
        self.creator = ""
        self.version = ""
        self.source = ""
        self.tags = ""

        self.key_count = 0
        self.overall_difficulty = 0

        self.timing_points = []
        self.hit_objects = []

class Osu:
    # Create an OsuFile from a given path to a .osu file
    # Returns an OsuFile, or None if the .osu file did not exist
    @staticmethod
    def create_from_path(fname):
        if exists(fname) and fname[-4:] == ".osu":
            content = ""
            with open(fname, "r+", encoding="utf-8") as file:
                content = file.read()

            # A .osu file is essentially a .ini file
            cfg = ConfigParser(allow_no_value=True, delimiters=":", comment_prefixes="//", strict=False)
            cfg.read_string("".join(content.split("\n", 2)[2:])) # start parsing on the [General] line to avoid MissingSectionHeaderError

            osu_file = OsuFile()

            # Check mode right away to ensure we're even dealing with an osu!mania map (mode must be 3)
            osu_file.mode = cfg.getint("General", "Mode")
            if osu_file.mode != 3:
                print("Not a valid osu!mania map.")
                return

            # Get metadata information and key count
            osu_file.audio_filename = cfg.get("General", "AudioFilename")
            osu_file.audio_lead_in  = cfg.getint("General", "AudioLeadIn")
            osu_file.preview_time   = cfg.getint("General", "PreviewTime")
            osu_file.special_style  = cfg.getint("General", "SpecialStyle")

            if cfg.has_option("Editor", "Bookmarks"):
                osu_file.bookmarks = [int(x) for x in cfg.get("Editor", "Bookmarks").split(",")]

            osu_file.title          = cfg.get("Metadata", "Title")
            osu_file.title_unicode  = cfg.get("Metadata", "TitleUnicode")
            osu_file.artist         = cfg.get("Metadata", "Artist")
            osu_file.artist_unicode = cfg.get("Metadata", "ArtistUnicode")
            osu_file.creator        = cfg.get("Metadata", "Creator")
            osu_file.version        = cfg.get("Metadata", "Version")
            osu_file.source         = cfg.get("Metadata", "Source")
            osu_file.tags           = cfg.get("Metadata", "Tags")

            osu_file.key_count          = cfg.getint("Difficulty", "CircleSize")
            osu_file.overall_difficulty = cfg.getfloat("Difficulty", "OverallDifficulty")

            # Taking advantage of ConfigParser's allow_no_value feature here
            # to easily get lists of the map's TimingPoints and HitObjects
            for t in cfg.items("TimingPoints"):
                parsed_timing_point = t[0].split(",")

                # Only append uninherited points (no SVs)
                if parsed_timing_point[6] == "1":
                    timing_point = OsuTimingPoint(
                        # very rarely the editor will spit out floating point time values, so double cast to be safe
                        time=int(float(parsed_timing_point[0])),
                        beat_length=float(parsed_timing_point[1]),
                        meter=int(parsed_timing_point[2]),
                        sample_set=int(parsed_timing_point[3]),
                        sample_index=int(parsed_timing_point[4]),
                        volume=int(parsed_timing_point[5]),
                        uninherited=("1" == parsed_timing_point[6]), # True if 1, False if 0
                        effects=int(parsed_timing_point[7])
                    )

                    osu_file.timing_points.append(timing_point)

            for h in cfg.items("HitObjects"):
                parsed_hit_object = (h[0]+":"+h[1]).split(",") # add missing colon before comma split
                x = int(parsed_hit_object[0])
                time = int(parsed_hit_object[2])
                type = int(parsed_hit_object[3])
                end_time = 0

                # osu!mania hold notes are formatted with an extra field
                # for the end_time of the note which doesn't exist otherwise
                if type & 128:
                    end_time = int(parsed_hit_object[5].split(":")[0])

                mania_hit_object = OsuHitObject(x, time, type, end_time)

                osu_file.hit_objects.append(mania_hit_object)

            # Prepend an OsuTimingPoint for any hit objects that maybe have
            # been placed before the first real OsuTimingPoint
            if len(osu_file.hit_objects) > 0:
                if osu_file.hit_objects[0].time < osu_file.timing_points[0].time:
                    osu_file.timing_points.insert(0, copy.copy(osu_file.timing_points[0]))
                    osu_file.timing_points[0].time = osu_file.hit_objects[0].time

            return osu_file
        else:
            return None