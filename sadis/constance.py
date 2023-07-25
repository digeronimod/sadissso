# Python
import datetime

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    '2019_2020_year_end': (datetime.date(2020, 6, 2), '2019-2020 School Year End'),
    '2019_2020_year_start': (datetime.date(2019, 8, 10), '2019-2020 School Year Start'),
    '2020_2021_year_end': (datetime.date(2021, 6, 2), '2020-2021 School Year End'),
    '2020_2021_year_start': (datetime.date(2020, 8, 10), '2020-2021 School Year Start'),
    '2021_2022_year_end': (datetime.date(2022, 6, 2), '2021-2022 School Year End'),
    '2021_2022_year_start': (datetime.date(2021, 8, 10), '2021-2022 School Year Start'),
    '2022_2023_year_end': (datetime.date(2023, 6, 2), '2022-2023 School Year End'),
    '2022_2023_year_start': (datetime.date(2022, 8, 10), '2022-2023 School Year Start'),
    '2023_2024_year_end': (datetime.date(2024, 6, 2), '2023-2024 School Year End'),
    '2023_2024_year_start': (datetime.date(2023, 8, 10), '2023-2024 School Year Start'),
    'bes_lead': ('4c28abf3-00ed-4776-8c03-dd490bcadb8d', 'Bunnell Elementary Lead Technician'),
    'bes_registrar': ('barnesb@flaglerschools.com', 'Bunnell Elementary Registrar'),
    'bes_agent': ('stovert@flaglerschools.com', 'Bunnell Elementary IS Agent'),
    'bes_iiq_team_id': ('2a773f37-4102-ea11-828b-0003ffe41fe2', 'Bunnell Elementary IIQ Team ID'),
    'bes_iiq_location_id': ('78d2335b-cd59-e811-80c3-000d3a012d41', 'Bunnell Elementary IIQ Location ID'),
    'btes_lead': ('54b3aaa1-fad6-4992-be0c-5d262f0da49e', 'Belle Terre Elementary Lead Technician'),
    'btes_registrar': ('meadel@flaglerschools.com', 'Belle Terre Elementary Registrar'),
    'btes_agent': ('bernhardb@flaglerschools.com', 'Belle Terre Elementary IS Agent'),
    'btes_iiq_team_id': ('421e3312-4102-ea11-828b-0003ffe41fe2', 'Belle Terre Elementary IIQ Team ID'),
    'btes_iiq_location_id': ('0e1c013e-cd59-e811-80c3-000d3a012d41', 'Belle Terre Elementary IIQ Location ID'),
    'btms_lead': ('28601bd1-501c-4118-a8dc-1eec4f93d1d9', 'Buddy Taylor Middle Lead Technician'),
    'btms_registrar': ('goicoecheak@flaglerschools.com', 'Buddy Taylor Middle Registrar'),
    'btms_agent': ('sorrentinot@flaglerschools.com', 'Buddy Taylor Middle IS Agent'),
    'btms_iiq_team_id': ('00e79be9-c6db-e911-b5e9-2818785cfb3e', 'Buddy Taylor Middle IIQ Team ID'),
    'btms_iiq_location_id': ('253cedcd-cd59-e811-80c3-000d3a012d41', 'Buddy Taylor Middle IIQ Location ID'),
    'collections_date': ('2021-2022', 'Current Collections Date'),
    'current_school_year_start': (datetime.date(2022, 8, 10), 'Current School Year Start'),
    'current_school_year_end': (datetime.date(2023, 5, 23), 'Current School Year End'),
    'current_school_year_abbrev': ('22-23', 'Current School Year Abbreviation'),
    'distributions_date': ('2022-2023', 'Current Distributions Date'),
    'dlmr_calendar_uuid': ('BB3RVNE5ELGOPXAJ', 'Calendly Event for DLMR to Sync'),
    'dlmr_calendly_global': ('https://calendly.com/tech-connect/dlm-device-pickup', 'Global Calendly Appointments'),
    'dlmr_calendly_tcd': ('https://calendly.com/tech-connect/tech-connect-in-person-appointment-at-gsb', 'URL for TCD Appointments'),
    'dlmr_calendly_mhs': ('https://calendly.com/tech-connect/tech-connect-device-and-support', 'URL for MHS Appointments'),
    'dlmr_calendly_fpc': ('https://calendly.com/tech-connect/fpchs-dlmr-device-pickup', 'URL for FPC Appointments'),
    'dlmr_calendar': (False, 'DLMR Calendar Invite (Global)', bool),
    'dlmr_calendar_secondary': (False, 'DLMR Calendar Invite (Secondary)', bool),
    'dlmr_closed': (True, 'Shutdown the DLMR for All Registrations'),
    'dlmr_summer_only': (False, 'DLMR can only be completed by Summer Program statused'),
    'dlmr_year_start': (datetime.date(2021, 5, 19), 'DLMR Start Date'),
    'expiration_bes': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for BES'),
    'expiration_btes': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for BTES'),
    'expiration_btms': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for BTMS'),
    'expiration_collections': (datetime.datetime(2021, 6, 2, 23, 59, 59), 'Expiration Date for Distributions'),
    'expiration_distribution': (datetime.datetime(2021, 8, 9, 23, 59, 59), 'Expiration Date for Distributions'),
    'expiration_fpc_senior': (datetime.datetime(2021, 5, 24, 23, 59, 59), 'Expiration Date for FPC Seniors'),
    'expiration_fpc_underclass': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for FPC Underclassmen'),
    'expiration_if': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for IF'),
    'expiration_itms': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for ITMS'),
    'expiration_mhs_senior': (datetime.datetime(2021, 5, 24, 23, 59, 59), 'Expiration Date for MHS Seniors'),
    'expiration_mhs_underclass': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for MHS Underclassmen'),
    'expiration_okes': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for OKES'),
    'expiration_res': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for RES'),
    'expiration_wes': (datetime.datetime(2021, 6, 3, 23, 59, 59), 'Expiration Date for WES'),
    'fpc_agent': ('santiagoj@flaglerschools.com', 'Flagler Palm Coast High IS Agent'),
    'fpc_lead': ('75ae59fa-4ccb-4ff8-94e3-aa3d07f6fcf1', 'Flagler Palm Coast High Lead Technician'),
    'fpc_registrar': ('kilionaf@flaglerschools.com', 'Flagler Palm Coast High Registrar'),
    'fpc_iiq_team_id': ('3267d11d-e3e9-ea11-8b03-281878210000', 'Flagler Palm Coast High IIQ Team ID'),
    'fpc_iiq_location_id': ('d25ffc02-ce59-e811-80c3-000d3a012d41', 'Flagler Palm Coast High IIQ Location ID'),
    'iiq_enabled': (True, 'Is IIQ enabled?'),
    'itms_agent': ('grushkinf@flaglerschools.com', 'Indian Trails Middle IS Agent'),
    'itms_lead': ('154103c7-3f44-4010-98e8-57a9aae4480b', 'Indian Trails Middle Lead Technician'),
    'itms_registrar': ('grantm@flaglerschools.com', 'Indian Trails Middle Registrar'),
    'itms_iiq_team_id': ('24c7b406-c8db-e911-b5e9-2818785cfb3e', 'Indian Trails Middle IIQ Team ID'),
    'itms_iiq_location_id': ('42d2e7e6-cd59-e811-80c3-000d3a012d41', 'Indian Trails Middle IIQ Location ID'),
    'mhs_agent': ('coatesa@flaglerschools.com', 'Matanzas High IS Agent'),
    'mhs_lead': ('f374a8ff-9ebd-456d-a441-fe816fdd1e7e', 'Matanzas High Lead Technician'),
    'mhs_registrar': ('ryank@flaglerschools.com', 'Matanzas High Registrar'),
    'mhs_iiq_team_id': ('aa4e6d35-e3e9-ea11-8b03-281878210000', 'Matanzas High IIQ Team ID'),
    'mhs_iiq_location_id': ('f827d955-ce59-e811-80c3-000d3a012d41', 'Matanzas High IIQ Location ID'),
    'msb_enabled': (True, 'Is MSB enabled?'),
    'okes_agent': ('olivar@flaglerschools.com', 'Old Kings Elementary IS Agent'),
    'okes_lead': ('fdb9892f-1c84-469d-880f-26e42119ad4d', 'Old Kings Elementary Lead Technician'),
    'okes_registrar': ('ackleyk@flaglerschools.com', 'Old Kings Elementary Registrar'),
    'okes_iiq_team_id': ('49e31ce0-4002-ea11-828b-0003ffe41fe2', 'Old Kings Elementary IIQ Team ID'),
    'okes_iiq_location_id': ('4b8f9079-cd59-e811-80c3-000d3a012d41', 'Old Kings Elementary IIQ Location ID'),
    'previous_school_year_abbrev': ('21-22', 'Previous School Year Abbreviation'),
    'res_agent': ('olivar@flaglerschools.com', 'Rymfire Elementary IS Agent'),
    'res_lead': ('0d05736c-1662-44d0-bfaf-f5876e336219', 'Rymfire Elementary Lead Technician'),
    'res_registrar': ('burnsp@flaglerschools.com', 'Rymfire Elementary Registrar'),
    'res_iiq_team_id': ('f20d9cc7-4002-ea11-828b-0003ffe41fe2', 'Rymfire Elementary IIQ Team ID'),
    'res_iiq_location_id': ('eeb94098-cd59-e811-80c3-000d3a012d41', 'Rymfire Elementary IIQ Location ID'),
    'sync_iiq': (datetime.datetime(2020, 1, 1, 15, 0, 0), 'Last date and time of sync with IncidentIQ'),
    'sync_edfi': (datetime.datetime(2020, 1, 1, 15, 0, 0), 'Last date and time of sync with Ed-Fi'),
    'THE_ANSWER': (42, 'The answer to life, the universe, and everything', int),
    'wes_agent': ('duttonj@flaglerschools.com', 'Wadsworth Elementary IS Agent'),
    'wes_lead': ('6ac9f0b4-f235-4bea-b555-9d0bb11f0ce9', 'Wadsworth Elementary Lead Technician'),
    'wes_registrar': ('ledekr@flaglerschools.com', 'Wadsworth Elementary Registrar'),
    'wes_iiq_team_id': ('dd627b96-4002-ea11-828b-0003ffe41fe2', 'Wadsworth Elementary IIQ Team ID'),
    'wes_iiq_location_id': ('454f98b1-cd59-e811-80c3-000d3a012d41', 'Wadsworth Elementary IIQ Location ID')
}
CONSTANCE_CONFIG_FIELDSETS = {
    'Digital Learning Movement': ('dlmr_closed', 'dlmr_summer_only', 'dlmr_year_start', 'dlmr_calendar', 'dlmr_calendar_secondary', 'dlmr_calendar_uuid', 'dlmr_calendly_global', 'dlmr_calendly_tcd', 'dlmr_calendly_mhs', 'dlmr_calendly_fpc'),
    'Belle Terre Elementary': ('btes_agent', 'btes_lead', 'btes_registrar', 'btes_iiq_team_id', 'btes_iiq_location_id'),
    'Buddy Taylor Middle': ('btms_agent', 'btms_lead', 'btms_registrar', 'btms_iiq_team_id', 'btms_iiq_location_id'),
    'Bunnell Elementary': ('bes_agent', 'bes_lead', 'bes_registrar', 'bes_iiq_team_id', 'bes_iiq_location_id'),
    'Collections/Distributions': ('expiration_collections', 'expiration_distribution', 'collections_date', 'distributions_date'),
    'Flagler Palm Coast High': ('fpc_agent', 'fpc_lead', 'fpc_registrar', 'fpc_iiq_team_id', 'fpc_iiq_location_id'),
    'Indian Trails Middle': ('itms_agent', 'itms_lead', 'itms_registrar', 'itms_iiq_team_id', 'itms_iiq_location_id'),
    'Matanzas High': ('mhs_agent', 'mhs_lead', 'mhs_registrar', 'mhs_iiq_team_id', 'mhs_iiq_location_id'),
    'Old Kings Elementary': ('okes_agent', 'okes_lead', 'okes_registrar', 'okes_iiq_team_id', 'okes_iiq_location_id'),
    'Other': ('THE_ANSWER', 'iiq_enabled', 'msb_enabled', 'sync_iiq', 'sync_edfi'),
    'Rymfire Elementary': ('res_agent', 'res_lead', 'res_registrar', 'res_iiq_team_id', 'res_iiq_location_id'),
    'School Settings': ('current_school_year_start', 'current_school_year_end', 'current_school_year_abbrev', 'previous_school_year_abbrev', '2019_2020_year_start', '2019_2020_year_end', '2020_2021_year_start', '2020_2021_year_end', '2021_2022_year_start', '2021_2022_year_end', '2022_2023_year_start', '2022_2023_year_end', '2023_2024_year_start', '2023_2024_year_end'),
    'Student Expirations': ('expiration_bes', 'expiration_btes', 'expiration_btms', 'expiration_fpc_senior', 'expiration_fpc_underclass', 'expiration_if', 'expiration_itms', 'expiration_mhs_senior', 'expiration_mhs_underclass', 'expiration_okes', 'expiration_res', 'expiration_wes'),
    'Wadsworth Elementary': ('wes_agent', 'wes_lead', 'wes_registrar', 'wes_iiq_team_id', 'wes_iiq_location_id')
}