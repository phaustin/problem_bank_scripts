---
title: OSUPv2p12_55
topic: Template
author: Jake Bobowksi
source: 2.12.55
template_version: 1.1
attribution: openstax-physics-vol2
outcomes:
- 19.2.3.0
- 19.2.3.1
- 19.3.2.0
- 19.3.2.1
- 19.6.1.0
- 19.6.1.1
difficulty:
- undefined
randomization:
- undefined
taxonomy:
- undefined
tags:
- OSUP
- volume 2
- chapter 12
- problem 55
- magnetic force
- solenoid
- centripetal acceleration
- circular motion
assets: null
server:
  imports: |
    import random;random.seed(111)
    import numpy as np
    import pandas as pd
    import problem_bank_helpers as pbh

    # Feedback params
    rtol = 0.03
    errorCheck = 'True'

    feedback_dict = {'vars': ['part1_ans'],
                     'stringData': ['I'],
                     'units': ['$~\mathrm{A}$']
                     }
  generate: |
    data2 = pbh.create_data2()

    # define bounds of the variables
    n = random.choice(np.linspace(10, 35, num = 6)) # cm^-1
    r = random.choice(np.linspace(1, 3, num = 21)) # cm
    v = random.choice(np.linspace(1, 3, num = 21))
    p = random.choice([4, 5, 6])

    # store the variables in the dictionary "params"
    data2["params"]["n"] = "{:.0f}".format(n)
    data2["params"]["r"] = "{:.2f}".format(r)
    data2["params"]["v"] = "{:.2f}".format(v)
    data2["params"]["p"] = "{:.0f}".format(p)

    # fix units
    n = n*100 # m^-1
    r = r/100 # m
    v = v*10**p # m/s

    # define some constants
    mu0 = 4e-7*np.pi
    m = 9.11e-31 # kg
    q = 1.6e-19 # C

    # calculate the correct
    I = m*v/(mu0*n*q*r) # A

    # define correct answers
    data2["correct_answers"]["part1_ans"] = I

    # Write the solution formatted using scientific notation while keeping 3 sig figs.
    data2["correct_answers"]["part1_ans_str"] = "{:.2e}".format(I)

    # Update the data object with a new dict
    data.update(data2)
  prepare: 'pass

    '
  parse: |
    # Call a function to check if the submitted answers should be re-expressed using scientific notation.
    for i,k in enumerate(feedback_dict['vars']):
        data["submitted_answers"][k + '_str'] = pbh.sigFigCheck(data["submitted_answers"][k], feedback_dict['stringData'][i], feedback_dict['units'][i])
  grade: |
    # Call a function to check for easily-identifiable errors.
    # The syntax is pbh.ErrorCheck(errorCheck, submittedAnswer, correctAnswer, LaTeXsyntax, relativeTolerance)
    # To enable error checking, set errorCheck = 'true'.

    for i,k in enumerate(feedback_dict['vars']):
        data["feedback"][k] = pbh.ErrorCheck(errorCheck, data["submitted_answers"][k], data["correct_answers"][k], feedback_dict['stringData'][i], rtol)
part1:
  type: number-input
  pl-customizations:
    weight: 1
    allow-blank: false
    show-correct-answer: false
    label: $I= $
    suffix: $\rm\ A$
    comparison: relabs
    rtol: 0.03
    atol: 0
substitutions:
  params:
    n: '15'
    r: '2.00'
    v: '2.50'
    p: '4'
  correct_answers:
    part1_ans: !!python/object/apply:numpy.core.multiarray.scalar
    - !!python/object/apply:numpy.dtype
      args:
      - f8
      - false
      - true
      state: !!python/tuple
      - 3
      - <
      - null
      - null
      - null
      - -1
      - -1
      - 0
    - !!binary |
      ZVy1Q2Xubj8=
    part1_ans_str: '3.78e-03'
---
# {{ params.vars.title }}

## Question Text

A solenoid with ${{ params.n }}$ turns per centimter carries a current $I$. An electron moves within the solenoid in a circle of radius ${{ params.r}}\textrm{ cm}$.
The plane of the circular motion is perpendicular to the axis of the solenoid.  The speed of the electron is ${{ params.v }}\times 10^{ {{ params.p }} }\textrm{ m/s}$.
What is the current $I$ in the solenoid?

### Answer Section

## Rubric

This should be hidden from students until after the deadline.

## Solution

This should never be revealed to students.

## Comments

These are random comments associated with this question.

## Attribution

Problem is from the [OpenStax University Physics Volume 2](https://openstax.org/details/books/university-physics-volume-2) textbook, licensed under the [CC-BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).<br>![Image representing the Creative Commons 4.0 BY license.](https://raw.githubusercontent.com/firasm/bits/master/by.png)