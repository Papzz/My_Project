LATVIAN_MONTHS = {
    '01': 'Janvāris',
    '02': 'Februāris',
    '03': 'Marts',
    '04': 'Aprīlis',
    '05': 'Maijs',
    '06': 'Jūnijs',
    '07': 'Jūlijs',
    '08': 'Augusts',
    '09': 'Septembris',
    '10': 'Oktobris',
    '11': 'Novembris',
    '12': 'Decembris',
}


def get_latvian_month(month_number):
    return LATVIAN_MONTHS.get(month_number, '')
