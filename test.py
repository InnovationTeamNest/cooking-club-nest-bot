# -*- coding: utf-8 -*-
from api import get_group, get_number_members_tuple, get_multiple_groups

if __name__ == "__main__":
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"