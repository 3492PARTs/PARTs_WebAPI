from scouting.models import ScoutFieldSchedule


def format_scout_field_schedule_entry(fs: ScoutFieldSchedule):
    return {
        'scout_field_sch_id': fs.scout_field_sch_id,
        'event_id': fs.event_id,
        'st_time': fs.st_time,
        'end_time': fs.end_time,
        'notification1': fs.notification1,
        'notification2': fs.notification2,
        'notification3': fs.notification3,
        'red_one_id': fs.red_one,
        'red_two_id': fs.red_two,
        'red_three_id': fs.red_three,
        'blue_one_id': fs.blue_one,
        'blue_two_id': fs.blue_two,
        'blue_three_id': fs.blue_three,
        'red_one_check_in': fs.red_one_check_in,
        'red_two_check_in': fs.red_two_check_in,
        'red_three_check_in': fs.red_three_check_in,
        'blue_one_check_in': fs.blue_one_check_in,
        'blue_two_check_in': fs.blue_two_check_in,
        'blue_three_check_in': fs.blue_three_check_in,
        'scouts': 'R1: ' +
                  ('' if fs.red_one is None else fs.red_one.first_name + ' ' + fs.red_one.last_name[0:1]) +
                  '\nR2: ' +
                  ('' if fs.red_two is None else fs.red_two.first_name + ' ' + fs.red_two.last_name[0:1]) +
                  '\nR3: ' +
                  ('' if fs.red_three is None else fs.red_three.first_name + ' ' + fs.red_three.last_name[
                                                                                   0:1]) +
                  '\nB1: ' +
                  ('' if fs.blue_one is None else fs.blue_one.first_name + ' ' + fs.blue_one.last_name[0:1]) +
                  '\nB2: ' +
                  ('' if fs.blue_two is None else fs.blue_two.first_name + ' ' + fs.blue_two.last_name[0:1]) +
                  '\nB3: ' +
                  ('' if fs.blue_three is None else fs.blue_three.first_name + ' ' + fs.blue_three.last_name[
                                                                                     0:1])
    }
