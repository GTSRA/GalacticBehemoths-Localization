# Translation Task Prompt

When I need you to translate missing keys, please follow these steps:

## 1. Generate Missing Translations
**Always prioritize using the virtual environment** (`.venv`, or `venv` if configured).
Run the coverage script to find all missing localization keys and output them to a JSON file:
```bash
.venv/bin/python scripts/check_translation_coverage.py -o data/missing_translations.json
```
*(Or activate the virtual environment via `source .venv/bin/activate` before running `python scripts/check_translation_coverage.py -o data/missing_translations.json`)*

## 2. Translate the Keys
Read the generated `data/missing_translations.json` file and translate the `original` Chinese text into English with your own capability.

Items in `missing_translations.json` can have two statuses:
* `"status": "missing"`: Newly added keys that do not have an English translation yet.
* `"status": "outdated"`: Keys that were previously translated, but whose original Chinese text has been updated.
  - `"original"` / `"new_original"`: The latest Chinese text to translate.
  - `"old_original"`: The previous Chinese text before the change, provided for context and diff reference.
  - For outdated items, provide an updated translation based on `new_original`.

### Mandatory Requirements:
* **No External Tools:** Do not use any external web scrapers or unauthorized external tools.
* **Schema Adherence:** Your final output MUST strictly match the JSON schema defined in `data/missing_translations_translated_schema.json`. It should be a JSON array of objects containing `file`, `key`, `original` (must be the updated/new original text), and `translation`.

* **Strict Glossary Compliance (Highest Priority):** 
  You MUST follow the project's official terminology definitions in [`data/glossary.json`](../data/glossary.json) and [`docs/glossary.md`](glossary.md).
  - **Characters & Factions:** 
    - 希诺 $\to$ `Xino` (Never use *Xinuo* or *Xilonen*)
    - 法拉 $\to$ `Fara`
    - 亚绒 $\to$ `Yarong`
    - 艾雅法拉 $\to$ `Eyjafjalla`
    - 白 $\to$ `Shiro`
    - 舰娘 / 艦娘 $\to$ `Shipgirl` (Never use *Kanmusu*)
    - 纯真智械 $\to$ `Innocent Machine`
    - Bruh系列 $\to$ `Bruh Series`
  - **Theme Scales & Mechanics:** 
    - 巨娘 / 巨大娘 $\to$ `Giantess`
    - 小人 $\to$ `Tiny person` (plural: `Tinies` or `Tiny people`)
    - 缩小人 $\to$ `Shrunken person`
    - 缩小城市 $\to$ `Shrunken city`
    - 尺度分级 $\to$ `Titan` (泰坦) / `Giant` (巨大) / `Tall` (高大) / `Normal` (常规) / `Small` (小型) / `Tiny` (微型) / `Micro` (微观) / `Macro` (宏观)
  - **Special Byproducts & Items:** 
    - 汗液 $\to$ `Sweat`
    - 足汗 $\to$ `Foot Sweat`
    - 爱液 $\to$ `Love fluid`
    - 消化液 $\to$ `Digestive fluid`
    - 神液 $\to$ `Divine fluid`
    - 体液 $\to$ `Bodily Fluids`
    - 胖次 $\to$ `Panties`
    - 核心元件 $\to$ `Core component`
    - 灵能罐头 $\to$ `The Psionic Can`
  - **Stellaris Vanilla Terms:**
    - 民事理念 $\to$ `Civic`
    - 特质 $\to$ `Trait`
    - 起源 $\to$ `Origin`
    - 飞升天赋 $\to$ `Ascension Perk`
    - 岗位 $\to$ `Job`
    - 区划 $\to$ `District`
    - 凝聚力 $\to$ `Unity`
* **Formatting & Preservation:**
  - Preserve all Paradox formatting and color codes (e.g. `§Y...§!`, `§R...§!`, `§M...§!`).
  - Preserve all variables and localisation macro links (e.g. `[Root.GetName]`, `$trait_xxx$`, `\n`).

## 3. Save Output
Save your translated JSON array to `data/missing_translations_translated.json`.

## 4. Apply Translations
Once translated, use the project application script (prioritizing the virtual environment `.venv`) to update the English localization files and synchronize `data/translation_lock.json`:
```bash
.venv/bin/python scripts/apply_translations_v2.py
```
*(Or `python scripts/apply_translations_v2.py` with the virtual environment activated)*

