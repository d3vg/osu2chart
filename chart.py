from math import ceil, floor

# Helpful conversion functions
def beat_length_to_bpm(beat_length):
    return 1 / beat_length * 60000

def x_to_key_column(x, key_count):
    return floor(x * key_count / 512)

class ChartFile:
    def __init__(self):
        self.song = {
            "Name": "",
            "Artist": "",
            "Charter": "",
            "Offset": 0,
            "Resolution": 192,
            "Player2": "bass",
            "Difficulty": 0,
            "PreviewStart": 0,
            "PreviewEnd": 0,
            "Genre": "rock",
            "MediaType": "cd",
            "GuitarStream": ""
        }
        self.sync_track = None
        self.events_track = None
        self.note_tracks = []

    def export(self, fname):
        with open(fname, "w+", encoding="utf-8") as file:
            file.write(str(self))

    def __str__(self):
        chart_string = "[Song]\n{\n"
        for k in self.song:
            if type(self.song[k]) is str and k != "Player2":
                chart_string += f"  {k} = \"{self.song[k]}\"\n"
            else:
                chart_string += f"  {k} = {self.song[k]}\n"

        chart_string += "}\n"

        chart_string += str(self.sync_track)
        
        for nt in self.note_tracks:
            chart_string += str(nt)

        return chart_string

class SyncTrackBPM:
    _identifier = "B"

    def __init__(self, bpm):
        self.bpm = round(bpm * 1000)

    def __str__(self):
        return f"{self._identifier} {self.bpm}"

class SyncTrackTS:
    _identifier = "TS"

    def __init__(self, ts):
        self.ts = ts

    def __str__(self):
        return f"{self._identifier} {self.ts}"

class NoteTrackNote:
    _identifier = "N"

    def __init__(self, note, hold_time):
        self.note = note
        self.hold_time = hold_time

    def __str__(self):
        return f"{self._identifier} {self.note} {self.hold_time}"

class NoteTrackSP:
    _identifier = "S"

    def __init__(self, note, hold_time):
        self.note = note
        self.hold_time = hold_time

    def __str__(self):
        return f"{self._identifier} {self.note} {self.hold_time}"

class ChartTrack:
    def __init__(self, name, resolution=192):
        self.name = name
        self.resolution = resolution
        self.track_objects = {}

    def _add_track_object(self, resolution_time, track_object):
        if resolution_time not in self.track_objects:
            self.track_objects.update({resolution_time: []})

        self.track_objects[resolution_time].append(track_object)

    """
    [self.name]
    {
      str(track_object)
      str(track_object)
      str(track_object)
      ...
    }
    """
    def __str__(self):
        track_string = f"[{self.name}]\n{{\n"
        for rt in self.track_objects:
            for track_object in self.track_objects[rt]:
                track_string += "  " + str(rt) + " = " + str(track_object) + "\n"

        track_string += "}\n"
 
        return track_string

# Returns a ChartTrack that represents the [SyncTrack] section of a .chart
# based off a given list of OsuTimingPoints and a resolution 
def _generate_sync_track(timing_points, resolution=192):
    sync_track = ChartTrack("SyncTrack", resolution)

    # The first timing_point is guaranteed and is eventually used as the offset in the .chart,
    # therefore we set the resolution_time to 0
    sync_track._add_track_object(0, SyncTrackTS(timing_points[0].meter))
    sync_track._add_track_object(0, SyncTrackBPM(beat_length_to_bpm(timing_points[0].beat_length)))

    previous_time = timing_points[0].time
    resolution_time = 0
    previous_beat_length = timing_points[0].beat_length

    if len(timing_points) > 1:
        for timing_point in timing_points[1:]:
            # Use the offset between the current and previous times
            # when calculating the resolution_time
            offset_time = timing_point.time - previous_time

            resolution_time += (sync_track.resolution * offset_time / previous_beat_length)

            # Make a quantized version of resolution_time to reduce off-snapped syncs
            quantized_resolution_time = round(resolution_time / 2) * 2

            sync_track._add_track_object(quantized_resolution_time, SyncTrackTS(timing_point.meter))
            sync_track._add_track_object(quantized_resolution_time, SyncTrackBPM(beat_length_to_bpm(timing_point.beat_length)))

            # Update previous time / beat_length values for the next timing_point
            previous_time = timing_point.time
            previous_beat_length = timing_point.beat_length

    return sync_track

# TODO: Use bookmarks to indicate section events
# NOTE: Don't feel there is too much of a need for this, so might add later
def _generate_events_track(timing_points, bookmarks, resolution=192):
    events_track = ChartTrack("Events", resolution)

    return events_track

# Returns a ChartTrack that represents a note track section of a .chart (e.g. [ExpertSingle])
# based off a name, given list of OsuTimingPoints, list of OsuHitObjects, key count, is co-op, and resolution
#
# Will return None if there are no hit objects in the list of OsuHitObjects
def _generate_note_track(name, timing_points, hit_objects, key_count, is_coop, resolution=192):
    note_track = ChartTrack(name, resolution)

    resolution_time = 0

    # Make sure that any hit_objects exist
    if len(hit_objects) > 0:
        hit_object_index = 0
        hit_object = hit_objects[hit_object_index]
        previous_hit_object_time = timing_points[0].time

        hit_object_count = len(hit_objects)
        timing_point_count = len(timing_points)
        finish_last_point = False

        previous_timing_point = timing_points[0]
        next_timing_point = timing_points[0]

        # TODO: Make this more understandable... it is way too complicated
        for t, timing_point in enumerate(timing_points):
            # Keep track of the next_timing_point
            if t < timing_point_count - 1:
                next_timing_point = timing_points[t+1]
            else:
                finish_last_point = True

            # When there is a timing point (BPM/TS change) between notes,
            # the resolution_time need to take in account the time
            # lost between the last note in the previous timing point
            # and the current timing point
            if previous_hit_object_time < timing_point.time:
                resolution_time += (note_track.resolution * (timing_point.time - previous_hit_object_time) / previous_timing_point.beat_length)
                
                # If there weren't any hit objects within the current timing point,
                # the current timing point will have to work as the previous hit object time
                # due to how offset_time and resolution_time are calculated below
                previous_hit_object_time = timing_point.time

            while (hit_object.time < next_timing_point.time and hit_object_index < hit_object_count) or finish_last_point:
                # Use the offset between the current and previous hit object times
                # when calculating the resolution_time
                offset_time = hit_object.time - previous_hit_object_time

                # Sustains
                hold_time = 0
                quantized_hold_time = 0
                if hit_object.end_time > 0:
                    hold_section_start_time = hit_object.time # The start time for a section of the sustain (each sustain is divided into "sections" by BPM changes)
                    hold_finish_last_point = False
                    hold_next_timing_point = timing_point

                    # Look at upcoming timing points to compensate for sustains that span over multiple BPM changes
                    for ht, hold_timing_point in enumerate(timing_points[t:], start=t):
                        if ht < timing_point_count - 1:
                            hold_next_timing_point = timing_points[ht+1]
                        else:
                            hold_finish_last_point = True

                        if hit_object.end_time > hold_next_timing_point.time and not hold_finish_last_point:
                            hold_time += note_track.resolution * ((hold_next_timing_point.time - hold_section_start_time) / hold_timing_point.beat_length)
                        else:
                            hold_time += note_track.resolution * ((hit_object.end_time - hold_section_start_time) / hold_timing_point.beat_length)
                            break

                        hold_section_start_time = hold_next_timing_point.time

                    # Make a quantized version of hold_time to reduce off-snapped sustains
                    quantized_hold_time = round(hold_time / 2) * 2

                # Add to resolution_time to get the time position of the note
                resolution_time += (note_track.resolution * offset_time / timing_point.beat_length)

                # Make a quantized version of resolution_time to reduce off-snapped notes
                quantized_resolution_time = round(resolution_time / 2) * 2

                # TODO: Organize this better, way too much duplicate code
                hit_object_column = x_to_key_column(hit_object.x, key_count)
                note_value = -1
                track_object = None

                # Co-op maps
                if key_count > 9:
                    key_mode = floor(key_count / 2)

                    # 2P side
                    if is_coop and hit_object_column >= key_mode:
                        if key_mode < 6:
                            note_value = hit_object_column - (key_mode * is_coop)
                            track_object = NoteTrackNote(note_value, quantized_hold_time)
                        else:
                            # Open note
                            if hit_object_column % key_mode == 0:
                                track_object = NoteTrackNote(7, quantized_hold_time)
                            # Starpower
                            elif hit_object_column % key_mode == 8:
                                track_object = NoteTrackSP(2, quantized_hold_time)
                            # GRYBO + Force + Tap
                            else:
                                note_value = hit_object_column - (key_mode * is_coop) - 1
                                track_object = NoteTrackNote(note_value, quantized_hold_time)
                    # 1P side
                    elif not is_coop and hit_object_column < key_mode:
                        if key_mode < 6:
                            note_value = hit_object_column - (key_mode * is_coop)
                            track_object = NoteTrackNote(note_value, quantized_hold_time)
                        else:
                            # Open note
                            if hit_object_column % key_mode == 0:
                                track_object = NoteTrackNote(7, quantized_hold_time)
                            # Starpower
                            elif hit_object_column % key_mode == 8:
                                track_object = NoteTrackSP(2, quantized_hold_time)
                            # GRYBO + Force + Tap
                            else:
                                note_value = hit_object_column - (key_mode * is_coop) - 1
                                track_object = NoteTrackNote(note_value, quantized_hold_time)
                # Single player maps
                else:
                    if key_count < 6:
                        note_value = hit_object_column
                        track_object = NoteTrackNote(note_value, quantized_hold_time)
                    else:
                        # Open note
                        if hit_object_column == 0:
                            track_object = NoteTrackNote(7, quantized_hold_time)
                        # Starpower
                        elif hit_object_column == 8:
                            track_object = NoteTrackSP(2, quantized_hold_time)
                        # GRYBO + Force + Tap
                        else:
                            note_value = hit_object_column - 1
                            track_object = NoteTrackNote(note_value, quantized_hold_time)
                
                if track_object is not None:
                    note_track._add_track_object(quantized_resolution_time, track_object)

                previous_hit_object_time = hit_object.time
                hit_object_index += 1

                # Break out after processing the last hit_object on the last timing_point
                if hit_object_index == hit_object_count:
                    finish_last_point = False
                    break

                # Update hit_object for next iteration of the while loop
                hit_object = hit_objects[hit_object_index]

            previous_timing_point = timing_point
    else:
        return None

    return note_track

class Chart:
    # Returns a Chart with the appropriate difficulties based off the given osu_files
    @staticmethod
    def create_from_osu(source_osu_file, resolution=192, preview_length=0, use_unicode_metadata=False, use_tags_as_genre=False, expert=None, hard=None, medium=None, easy=None):
        chart_file = ChartFile()

        if use_unicode_metadata:
            chart_file.song["Name"] = source_osu_file.title_unicode
            chart_file.song["Artist"] = source_osu_file.artist_unicode
        else:
            chart_file.song["Name"] = source_osu_file.title
            chart_file.song["Artist"] = source_osu_file.artist

        chart_file.song["Charter"] = source_osu_file.creator

        chart_file.song["Offset"] = round(source_osu_file.timing_points[0].time / 1000, 3)
        chart_file.song["Resolution"] = resolution
        chart_file.song["Difficulty"] = floor(source_osu_file.overall_difficulty)

        # preview_time is -1 when not set in the osu! editor
        if source_osu_file.preview_time < 0:
            chart_file.song["PreviewStart"] = 0
        else:
            chart_file.song["PreviewStart"] = round(source_osu_file.preview_time / 1000, 3)

        # Set to 0 so the preview still plays and isn't literally a no length preview
        if preview_length == 0:
            chart_file.song["PreviewEnd"] = 0
        else:
            chart_file.song["PreviewEnd"] = chart_file.song["PreviewStart"] + preview_length

        if use_tags_as_genre:
            chart_file.song["Genre"] = source_osu_file.tags

        chart_file.song["GuitarStream"] = source_osu_file.audio_filename

        chart_file.sync_track = _generate_sync_track(source_osu_file.timing_points, chart_file.song["Resolution"])
        chart_file.events_track = _generate_events_track(source_osu_file.timing_points, source_osu_file.bookmarks, chart_file.song["Resolution"])

        if expert is not None:
            chart_file.note_tracks.append(_generate_note_track("ExpertSingle", expert.timing_points, expert.hit_objects, expert.key_count, False, chart_file.song["Resolution"]))
            if expert.key_count > 9:
                chart_file.note_tracks.append(_generate_note_track("ExpertDoubleGuitar", expert.timing_points, expert.hit_objects, expert.key_count, True, chart_file.song["Resolution"]))
        if hard is not None:
            chart_file.note_tracks.append(_generate_note_track("HardSingle", hard.timing_points, hard.hit_objects, hard.key_count, False, chart_file.song["Resolution"]))
            if hard.key_count > 9:
                chart_file.note_tracks.append(_generate_note_track("HardDoubleGuitar", hard.timing_points, hard.hit_objects, hard.key_count, True, chart_file.song["Resolution"]))
        if medium is not None:
            chart_file.note_tracks.append(_generate_note_track("MediumSingle", medium.timing_points, medium.hit_objects, medium.key_count, False, chart_file.song["Resolution"]))
            if medium.key_count > 9:
                chart_file.note_tracks.append(_generate_note_track("MediumDoubleGuitar", medium.timing_points, medium.hit_objects, medium.key_count, True, chart_file.song["Resolution"]))
        if easy is not None:
            chart_file.note_tracks.append(_generate_note_track("EasySingle", easy.timing_points, easy.hit_objects, easy.key_count, False, chart_file.song["Resolution"]))
            if easy.key_count > 9:
                chart_file.note_tracks.append(_generate_note_track("EasyDoubleGuitar", easy.timing_points, easy.hit_objects, easy.key_count, True, chart_file.song["Resolution"]))

        return chart_file