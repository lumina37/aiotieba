# -*- coding:utf-8 -*-
__all__ = [
    'JSON_DECODER',
]

import json


def _json_decoder_hook(_dict):
    for key, value in _dict.items():
        if not value:
            _dict[key] = None
    return _dict


JSON_DECODER = json.JSONDecoder(object_hook=_json_decoder_hook)
