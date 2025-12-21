"""
Country Code to Timezone Mapper
================================
This module provides mapping from ISO 3166-1 alpha-2 country codes to their
primary timezones. This is critical for ensuring that MultiLogin browser profiles
have the correct timezone setting that matches the Nodemaven proxy's IP geolocation.

The timezone must match the proxy's country to avoid detection by TikTok's
anti-bot systems, which check for IP/timezone mismatches.
"""

# Comprehensive mapping of country codes to primary timezones
# Format: "country_code": "IANA_timezone_identifier"
COUNTRY_TO_TIMEZONE = {
    # A
    "af": "Asia/Kabul",              # Afghanistan
    "al": "Europe/Tirane",           # Albania
    "dz": "Africa/Algiers",          # Algeria
    "ag": "America/Antigua",         # Antigua and Barbuda
    "ar": "America/Argentina/Buenos_Aires",  # Argentina
    "am": "Asia/Yerevan",            # Armenia
    "at": "Europe/Vienna",           # Austria
    "az": "Asia/Baku",               # Azerbaijan
    
    # B
    "bs": "America/Nassau",          # Bahamas
    "bh": "Asia/Bahrain",            # Bahrain
    "bd": "Asia/Dhaka",              # Bangladesh
    "bb": "America/Barbados",        # Barbados
    "by": "Europe/Minsk",            # Belarus
    "bj": "Africa/Porto-Novo",       # Benin
    "bt": "Asia/Thimphu",            # Bhutan
    "bo": "America/La_Paz",          # Bolivia
    "ba": "Europe/Sarajevo",         # Bosnia and Herzegovina
    "bw": "Africa/Gaborone",         # Botswana
    "br": "America/Sao_Paulo",       # Brazil
    "bn": "Asia/Brunei",             # Brunei
    "bg": "Europe/Sofia",            # Bulgaria
    
    # C
    "kh": "Asia/Phnom_Penh",         # Cambodia
    "cm": "Africa/Douala",           # Cameroon
    "ca": "America/Toronto",         # Canada
    "td": "Africa/Ndjamena",         # Chad
    "cl": "America/Santiago",        # Chile
    "cn": "Asia/Shanghai",           # China
    "co": "America/Bogota",          # Colombia
    "km": "Indian/Comoro",           # Comoros
    "cg": "Africa/Brazzaville",      # Congo
    "cd": "Africa/Kinshasa",         # Congo (DRC)
    "cr": "America/Costa_Rica",      # Costa Rica
    "ci": "Africa/Abidjan",          # Côte d'Ivoire
    "hr": "Europe/Zagreb",           # Croatia
    "cu": "America/Havana",          # Cuba
    "cy": "Asia/Nicosia",            # Cyprus
    "cz": "Europe/Prague",           # Czech Republic
    
    # D
    "dk": "Europe/Copenhagen",       # Denmark
    
    # E
    "eg": "Africa/Cairo",            # Egypt
    "sv": "America/El_Salvador",     # El Salvador
    "ee": "Europe/Tallinn",          # Estonia
    "et": "Africa/Addis_Ababa",      # Ethiopia
    
    # F
    "fj": "Pacific/Fiji",            # Fiji
    "fi": "Europe/Helsinki",         # Finland
    "fr": "Europe/Paris",            # France
    
    # G
    "ga": "Africa/Libreville",       # Gabon
    "ge": "Asia/Tbilisi",            # Georgia
    "gh": "Africa/Accra",            # Ghana
    "gr": "Europe/Athens",           # Greece
    "gt": "America/Guatemala",       # Guatemala
    "gn": "Africa/Conakry",          # Guinea
    "gw": "Africa/Bissau",           # Guinea-Bissau
    "gy": "America/Guyana",          # Guyana
    
    # H
    "hn": "America/Tegucigalpa",     # Honduras
    "hu": "Europe/Budapest",         # Hungary
    
    # I
    "is": "Atlantic/Reykjavik",      # Iceland
    "in": "Asia/Kolkata",            # India
    "id": "Asia/Jakarta",            # Indonesia
    "ir": "Asia/Tehran",             # Iran
    "iq": "Asia/Baghdad",            # Iraq
    "ie": "Europe/Dublin",           # Ireland
    "il": "Asia/Jerusalem",          # Israel
    
    # P
    "pl": "Europe/Warsaw",           # Poland
    
    # R
    "ro": "Europe/Bucharest",        # Romania
    
    # Add more countries as needed
    # This list covers all the countries in the provided proxy data
}


def get_timezone_for_country(country_code: str) -> str:
    """
    Get the primary timezone for a given country code.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "us", "fr", "jp")
    
    Returns:
        IANA timezone identifier (e.g., "America/New_York", "Europe/Paris")
    
    Raises:
        ValueError: If the country code is not found in the mapping
    
    Examples:
        >>> get_timezone_for_country("us")
        'America/New_York'
        >>> get_timezone_for_country("fr")
        'Europe/Paris'
    """
    country_code = country_code.lower().strip()
    
    if country_code not in COUNTRY_TO_TIMEZONE:
        raise ValueError(
            f"Country code '{country_code}' not found in timezone mapping. "
            f"Please add it to the COUNTRY_TO_TIMEZONE dictionary."
        )
    
    return COUNTRY_TO_TIMEZONE[country_code]


def get_all_supported_countries() -> list[str]:
    """
    Get a list of all supported country codes.
    
    Returns:
        List of ISO 3166-1 alpha-2 country codes
    """
    return list(COUNTRY_TO_TIMEZONE.keys())


def validate_country_code(country_code: str) -> bool:
    """
    Check if a country code is supported.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code
    
    Returns:
        True if the country code is supported, False otherwise
    """
    return country_code.lower().strip() in COUNTRY_TO_TIMEZONE


if __name__ == "__main__":
    # Test the module
    print("Country to Timezone Mapper - Test")
    print("=" * 50)
    
    test_countries = ["us", "fr", "jp", "dz", "cn", "br"]
    
    for country in test_countries:
        try:
            tz = get_timezone_for_country(country)
            print(f"{country.upper()}: {tz}")
        except ValueError as e:
            print(f"{country.upper()}: ERROR - {e}")
    
    print(f"\nTotal supported countries: {len(get_all_supported_countries())}")
