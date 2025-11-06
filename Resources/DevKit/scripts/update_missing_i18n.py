#!/usr/bin/env python3
"""
Update missing i18n translations in Localizable.xcstrings.
This script adds missing English localizations and fixes 'new' state translations.
"""

import json
import sys
import os

NEW_STRINGS: dict[str, dict[str, str]] = {
    "Proactive Memory": {"zh-Hans": "主动提供记忆"},
    "When enabled, FlowDown will include stored memories in system prompts and Shortcuts inference even if memory tools are disabled.": {
        "zh-Hans": "开启后，即使未启用记忆工具，FlowDown 也会在系统提示词与快捷指令推理中提供已存储的记忆。"
    },
    "Proactive Memory Context": {"zh-Hans": "主动提供的记忆摘要"},
    "Choose how FlowDown proactively shares stored memories with the model during conversations and Shortcuts automations.": {
        "zh-Hans": "选择 FlowDown 在对话与快捷指令自动化中向模型主动提供记忆的方式。"
    },
    "Off": {"zh-Hans": "关闭"},
    "Past Day": {"zh-Hans": "1 天内"},
    "Past Week": {"zh-Hans": "1 周内"},
    "Past Month": {"zh-Hans": "1 个月内"},
    "Past Year": {"zh-Hans": "1 年内"},
    "Latest 15 Items": {"zh-Hans": "最近 15 项"},
    "Latest 30 Items": {"zh-Hans": "最近 30 项"},
    "All Memories": {"zh-Hans": "所有"},
    "Proactive memory sharing is disabled.": {"zh-Hans": "已关闭主动提供记忆。"},
    "Memories saved within the past 24 hours.": {"zh-Hans": "包含过去 24 小时内保存的记忆。"},
    "Memories saved within the past 7 days.": {"zh-Hans": "包含过去 7 天内保存的记忆。"},
    "Memories saved within the past 30 days.": {"zh-Hans": "包含过去 30 天内保存的记忆。"},
    "Memories saved within the past year.": {"zh-Hans": "包含过去一年内保存的记忆。"},
    "The most recent 15 memories.": {"zh-Hans": "包含最近的 15 条记忆。"},
    "The most recent 30 memories.": {"zh-Hans": "包含最近的 30 条记忆。"},
    "All stored memories.": {"zh-Hans": "包含所有已存储的记忆。"},
    "Scope: %@": {"zh-Hans": "范围：%@"},
    "%d. [%@] %@": {"zh-Hans": "%d. [%@] %@"},
    "This summary is provided automatically according to the user's proactive memory setting, even when memory tools are disabled.": {
        "zh-Hans": "该摘要根据用户的主动记忆设置自动提供，即使记忆工具未启用也会附带。"
    },
    "A proactive memory summary has been provided above according to the user's setting. Treat it as reliable context and keep it updated through memory tools when necessary.": {
        "zh-Hans": "根据用户的设置，上方已提供主动记忆摘要。请将其视为可靠的上下文，并在需要时通过记忆工具保持更新。"
    },
}

def update_translations(file_path):
    """Update missing translations in the xcstrings file."""
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {file_path}: {e}")
        sys.exit(1)
    
    strings = data['strings']

    # Ensure new strings exist with provided translations
    for key, translations in NEW_STRINGS.items():
        entry = strings.setdefault(key, {})
        if entry.get('shouldTranslate') is False:
            entry.pop('shouldTranslate', None)

        locs = entry.setdefault('localizations', {})
        locs.setdefault('en', {
            'stringUnit': {
                'state': 'translated',
                'value': key,
            }
        })

        for language, value in translations.items():
            locs[language] = {
                'stringUnit': {
                    'state': 'translated',
                    'value': value,
                }
            }

    # Determine all languages present in the file (excluding ones marked shouldTranslate=false)
    languages: set[str] = set()
    for value in strings.values():
        locs = value.get('localizations', {})
        for lang in locs.keys():
            languages.add(lang)

    # Ensure English is always part of the language set
    languages.add('en')

    # Count changes
    added_count = 0
    fixed_count = 0
    filled_count = 0
    
    # Iterate through all strings
    for key, value in strings.items():
        # Skip strings marked as shouldTranslate=false
        if not value.get('shouldTranslate', True):
            continue
        
        # Ensure dictionary exists for modifications
        if 'localizations' not in value:
            value['localizations'] = {}

        locs = value['localizations']

        # Check if 'en' localization is missing
        if 'en' not in locs:
            locs['en'] = {
                'stringUnit': {
                    'state': 'translated',
                    'value': key
                }
            }
            added_count += 1

        # Ensure English localization is properly marked
        en_loc = locs['en']
        en_string_unit = en_loc.setdefault('stringUnit', {})
        if en_string_unit.get('state') == 'new':
            if not en_string_unit.get('value', '').strip():
                en_string_unit['value'] = key
            en_string_unit['state'] = 'translated'
            fixed_count += 1
        english_value = en_string_unit.get('value', key)

        # Fill missing localizations for other languages using English as fallback
        for language in languages:
            if language == 'en':
                continue

            string_unit = locs.get(language, {}).get('stringUnit')
            current_value = string_unit.get('value').strip() if string_unit and string_unit.get('value') else ''
            current_state = string_unit.get('state') if string_unit else None

            if language not in locs or not current_value:
                locs[language] = {
                    'stringUnit': {
                        'state': 'translated',
                        'value': english_value
                    }
                }
                filled_count += 1
            elif current_state == 'new':
                locs[language]['stringUnit']['state'] = 'translated'
                if not current_value:
                    locs[language]['stringUnit']['value'] = english_value
                filled_count += 1
    
    # Write the updated file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully updated {file_path}")
        print(f"   - Added {added_count} missing English localizations")
        print(f"   - Fixed {fixed_count} 'new' state translations")
        print(f"   - Filled {filled_count} fallback localizations")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Default path to the Localizable.xcstrings file
    default_file_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 
        'FlowDown', 
        'Resources', 
        'Localizable.xcstrings'
    )
    
    # Allow overriding the file path via command line argument
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    
    print(f"📝 Updating translations in: {file_path}")
    update_translations(file_path)
