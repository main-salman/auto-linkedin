"""
Version information for Auto LinkedIn
"""

VERSION = {
    'major': 0,
    'minor': 1,
    'patch': 0,
    'release': 'alpha',
    'build': 1
}

def get_version_string():
    """Get the version string in format major.minor.patch-release.build"""
    v = VERSION
    version_str = f"{v['major']}.{v['minor']}.{v['patch']}"
    
    if v['release']:
        version_str += f"-{v['release']}"
    
    if v['build']:
        version_str += f".{v['build']}"
    
    return version_str

__version__ = get_version_string() 