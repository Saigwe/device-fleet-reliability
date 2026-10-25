# Survival and replacement forecast

Hard drives with power-on hours: 347,650; failures this quarter: 1,027. Quarter ends 2026-03-31.

## Share of drives still working at each age (Kaplan-Meier, left-truncated)

|                 |   1 yr |   2 yr |   3 yr |   4 yr |   5 yr |   6 yr |   7 yr |   8 yr |
|:----------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| All hard drives |  0.99  |  0.984 |  0.979 |  0.97  |  0.959 |  0.948 |  0.924 |  0.919 |
| HGST            |  0.992 |  0.978 |  0.978 |  0.908 |  0.896 |  0.873 |  0.847 |  0.841 |
| Seagate         |  0.986 |  0.98  |  0.979 |  0.978 |  0.973 |  0.96  |  0.95  |  0.949 |
| Toshiba         |  0.989 |  0.979 |  0.971 |  0.955 |  0.944 |  0.937 |  0.924 |  0.916 |
| WDC             |  0.985 |  0.982 |  0.978 |  0.956 |  0.93  |  0.929 |  0.929 |  0.929 |

## Expected failures in the next 90 days, by model (top 15)

Drives in service at quarter end: 342,246. Expected failures next quarter, whole fleet: **914**.

| model                | manufacturer   | curve        |   drives_in_service |   median_age_years |   expected_failures_next_quarter |   per_1000_drives |
|:---------------------|:---------------|:-------------|--------------------:|-------------------:|---------------------------------:|------------------:|
| HGST HUH721212ALE604 | HGST           | model        |               13077 |                5   |                            131.6 |             10.06 |
| TOSHIBA MG08ACA16TA  | Toshiba        | model        |               39718 |                2.6 |                            107.9 |              2.72 |
| ST12000NM0008        | Seagate        | model        |               18420 |                6   |                             94.2 |              5.11 |
| ST8000NM0055         | Seagate        | model        |               13047 |                8.7 |                             86.1 |              6.6  |
| TOSHIBA MG07ACA14TA  | Toshiba        | model        |               37148 |                5.4 |                             78.6 |              2.12 |
| HGST HUH721212ALN604 | HGST           | manufacturer |                9557 |                7   |                             50.9 |              5.33 |
| ST24000NM002H        | Seagate        | model        |                9323 |                0.8 |                             49.1 |              5.27 |
| WDC WUH721816ALE6L4  | WDC            | model        |               26706 |                3.1 |                             49   |              1.83 |
| WDC WUH722222ALE6L4  | WDC            | model        |               45501 |                1.4 |                             44.7 |              0.98 |
| ST16000NM001G        | Seagate        | model        |               34587 |                3.9 |                             37.7 |              1.09 |
| TOSHIBA MG10ACA20TE  | Toshiba        | model        |               20404 |                1   |                             37.1 |              1.82 |
| TOSHIBA MG08ACA16TE  | Toshiba        | model        |                6238 |                4.5 |                             25.1 |              4.02 |
| ST12000NM001G        | Seagate        | model        |               13157 |                5.3 |                             23.3 |              1.77 |
| WDC WUH721816ALE6L0  | WDC            | manufacturer |                2970 |                4.4 |                             21.9 |              7.37 |
| ST8000DM002          | Seagate        | model        |                6891 |                0.6 |                             15   |              2.18 |
