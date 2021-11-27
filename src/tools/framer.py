import cv2

from .stats import Stats

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
FONT_COLOR_WHITE = (255, 255, 255)
FONT_COLOR_RED = (0, 0, 255)
line_type = 2


def add_stats_to_frame(stats: Stats, frame):
    cv2.putText(frame, 'Flight time: %d' % stats.get_tof(),
                (10, 500),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Time: %d s' % stats.get_time(),
                (10, 540),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Barometer: %.1f' % stats.get_baro(),
                (10, 580),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Temp: %.1f' % stats.get_temp(),
                (10, 620),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Battery: %d %%' % stats.get_bat(),
                (10, 660),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Altitude: %.1f' % stats.get_height(),
                (10, 700),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    return frame


def add_navigation_info_to_frame(info, frame):
    if info['autonomous_flight']:
        cv2.putText(frame, 'Autonomous Flight',
                    (10, 30),
                    font,
                    font_scale,
                    FONT_COLOR_RED,
                    line_type)
    cv2.putText(frame, 'Yaw: ' + str(info['yaw_reaction']),
                (10, 70),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Throttle: ' + str(info['throttle_reaction']),
                (10, 110),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Pitch: ' + str(info['pitch_reaction']),
                (10, 150),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)
    cv2.putText(frame, 'Flying' if info['flying'] else 'Not flying',
                (492, 30),
                font,
                font_scale,
                FONT_COLOR_WHITE,
                line_type)

    return frame
