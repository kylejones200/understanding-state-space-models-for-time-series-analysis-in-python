# Understanding State Space Models for Time Series Analysis in Python

This folder contains code and resources for the Medium article:
[Understanding State Space Models for Time Series Analysis in Python](https://medium.com/@kylejones_47003/understanding-state-space-models-for-time-series-analysis-in-python-1ceaa48753c2)

## Business context

Time series data is (usually) messy. When you look at a chart, you know there's a pattern underneath the jittery line. But it's hard to see.

State space models help pull that pattern out by separating the hidden structure from the observed noise. You model both the signal and the noise. One equation tracks how the underlying process changes. The other explains how that process produces what you actually measure.

Think of it as a system with two layers: The state layer describes the smooth, unobserved process --- the real trend. The observation layer describes the noisy version of that trend you see in the data.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).