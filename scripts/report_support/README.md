# Report validation support

These files are copied from the user's SiM MARKET LAB v6.2 report-generation materials ZIP:

- `10_calculation_reference.py`
- `11_validate_report_bundle.py` → `bundle_validator.py`
- `09_report_bundle_schema_v1.json` → `report_bundle.schema.json`

They use Python's standard library only. `scripts/validate_report_bundles.py` connects their arithmetic, references, dates, probabilities and HTML checks to the published site data. The schema is retained for independent JSON Schema checks; it introduces no runtime dependency.

Templates and original generation rules remain in the user-provided materials. Do not weaken these checks to publish incomplete reports.
