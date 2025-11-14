# Business Documentation

This folder contains business rules, calculation methodologies, and data mapping for the IEDI (Digital Exposure Index in the Press) system.

## Documentation Index

### IEDI Methodology

**[METODOLOGIA_IEDI.md](./METODOLOGIA_IEDI.md)** - Complete IEDI methodology including calculation formulas, weighting system, reach group classification, sentiment analysis, and balancing mechanisms. This is the final adapted version without spokesperson and image variables.

### Data Integration

**[MAPEAMENTO_BRANDWATCH.md](./MAPEAMENTO_BRANDWATCH.md)** - Complete mapping between Brandwatch API data and IEDI system entities, including field transformations, data extraction patterns, and integration workflows.

### Visualization

**[FORMULAS_POWERBI.md](./FORMULAS_POWERBI.md)** - DAX formulas and calculated measures for Power BI dashboards, enabling IEDI metrics visualization and analysis.

## Key Concepts

### IEDI Calculation

The IEDI (Digital Exposure Index in the Press) measures bank presence in Brazilian digital media through:

- **Presence variables**: Title, Subtitle (conditional), Relevant Media Outlet, Niche Media Outlet
- **Reach classification**: Groups A, B, C, D based on monthly traffic
- **Sentiment adjustment**: Positive, Neutral, Negative
- **Balancing**: Proportion of positive mentions across banks
- **Dynamic denominators**: 286/366 for Group A, 280/360 for other groups

### Reach Groups

- **Group A**: > 29 million visits/month (weight 91)
- **Group B**: 11-29 million visits/month (weight 85)
- **Group C**: 500k-11 million visits/month (weight 24)
- **Group D**: < 500k visits/month (weight 20)

### Data Sources

The system integrates with **Brandwatch** social listening platform to collect mentions from digital media outlets, applying the IEDI methodology to calculate exposure indices for each bank.

## Navigation

- [← Back to root](../../README.md)
- [→ Architecture Documentation](../architecture/README.md)
