---
title: Multi-part Question
topic: Template
author: Firas Moosvi
source: original
template_version: 1.1
attribution: standard
outcomes:
- 6.1.1.0
- 6.1.1.1
difficulty:
- undefined
randomization:
- undefined
taxonomy:
- undefined
tags:
- unknown
assets:
- test1.png
- test2.png
part1:
  type: number-input
  label: $d=$
  pl-customizations:
    allow-blank: true
    weight: 1
part2:
  type: multiple-choice
  pl-customizations:
    weight: 1
substitutions:
  params:
    vars:
      name: Maya
      vehicle: a unicycle
      title: Distance travelled
      units: m/s
    v: 5
    t: 6
    part2:
      ans1:
        value: 42
      ans2:
        value: 30
      ans3:
        value: 11
      ans4:
        value: 0.8333333333333334
      ans5:
        value: -1
      ans6:
        value: -1.3
---
# {{ params.vars.title }}
This part of the question is common to both Parts 1 and 2.

<img src="test1.png" width=400>

## Part 1

{{ params.vars.name }} is traveling on {{ params.vars.vehicle }} at {{ params.v }} {{ params.vars.units }}.
How far does {{ vars.name }} travel in {{ params.t }} seconds, assuming they continue at the same velocity?

<img src="test2.png" width=400>

### Answer Section

Please enter in a numeric value in {{ params.vars.units }}.

## Part 2

{{ params.vars.name }} is traveling on {{ params.vars.vehicle }} at {{ params.v }} {{ params.vars.units }}.
How far does {{ params.vars.name }} travel in {{ params.t }} seconds, assuming they continue at the same velocity?

### Answer Section

- {{ params.part2.ans1.value}} {{ params.vars.units}}
- {{ params.part2.ans2.value}} {{ params.vars.units}}
- {{ params.part2.ans3.value}} {{ params.vars.units}}
- {{ params.part2.ans4.value}} {{ params.vars.units}}
- {{ params.part2.ans5.value}} {{ params.vars.units}}
- {{ params.part2.ans6.value}} {{ params.vars.units}}

## Attribution

Problem is licensed under the [CC-BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/).<br> ![The Creative Commons 4.0 license requiring attribution-BY, non-commercial-NC, and share-alike-SA license.](https://raw.githubusercontent.com/firasm/bits/master/by-nc-sa.png)