Exparser models (both reference parsing and reference extraction) are trained on research papers in German as well as English language.

The following evaluation results are based on the corpus of 125 research papers from German language including the research papers containing references found in the footnotes and 100 research papers from English language.
Separate evaluation was performed for both German and English language dataset.


Exparser Reference identification results: (10 fold cross validation)

**Exparser German Dataset**


| Model         | Precision   | Recall      | F1          |
|-------------|-------------|-------------|-------------|
|  Exparser  | 0.69 | 0.89 | 0.78 |



1 line= First line of the reference.

I line= Intermediate line of the reference.

L line= Last line of the reference.

| Precision |        |        | Recall |        |        | F1 Score |        |        |
|-----------|--------|--------|--------|--------|--------|----------|--------|--------|
| 1 Line    | I Line | L Line | 1 Line | I Line | L Line | 1 Line   | I Line | L Line |
| 0.73      | 0.51   | 0.78   | 0.84   | 0.84   | 0.86   | 0.78     | 0.64   | 0.79   |


Exparser Reference parsing results: (10 fold cross validation)


**Exparser model evaluation on Exgoldstandard English Dataset**

| Tag         | Precision   | Recall      | F1          |
|-------------|-------------|-------------|-------------|
| publisher   | 0.959086477 | 0.845181313 | 0.89728132  |
| last page       | 0.993896063 | 0.984151736 | 0.9889821   |
| surname     | 0.951610043 | 0.884536717 | 0.91505436  |
| article-title       | 0.931791929 | 0.972769867 | 0.95151199  |
| url         | 0.965273268 | 0.763906669 | 0.808867549 |
| volume      | 0.95576658  | 0.937542063 | 0.945621057 |
| source      | 0.942626564 | 0.83490314  | 0.883653533 |
| given-names | 0.941450873 | 0.911911429 | 0.925533171 |
| editor      | 0.897915808 | 0.778200721 | 0.832358207 |
| first page       | 0.997159664 | 0.980429599 | 0.988697629 |
| year        | 0.944322999 | 0.933497319 | 0.938589647 |
| identifier  | 0.960358176 | 0.70076969  | 0.733457182 |
| issue       | 0.958618872 | 0.888918427 | 0.922161952 |
| other       | 0.846494385 | 0.722210955 | 0.776731361 |




**Exparser model evaluation on Exgoldstandard German Dataset**

| Tag         | Precision   | Recall      | F1          |
|-------------|-------------|-------------|-------------|
| publisher   | 0.964192636 | 0.81064742  | 0.875111434 |
| last page       | 0.991129788 | 0.962046788 | 0.976161105 |
| surname     | 0.90994633  | 0.787478211 | 0.843367591 |
| article-title       | 0.893704304 | 0.960605016 | 0.925422401 |
| url         | 0.996033448 | 0.800261321 | 0.880681245 |
| volume      | 0.932098238 | 0.78021711  | 0.847791857 |
| source      | 0.890182663 | 0.748975755 | 0.810636528 |
| given-names | 0.8900896   | 0.823056487 | 0.854994087 |
| editor      | 0.877913835 | 0.75151039  | 0.807626961 |
| first page       | 0.979024701 | 0.938542128 | 0.958159757 |
| year        | 0.904064843 | 0.90138347  | 0.902640056 |
| identifier  | 0.902012681 | 0.705569486 | 0.753663066 |
| issue       | 0.964353559 | 0.703203661 | 0.798748542 |
| other       | 0.848551117 | 0.73500243  | 0.78503847  |


