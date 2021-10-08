# Correcteur d'orthographe
La vraisemblance de chaque candidat *c* étant donné le mot entré *w* est donnée par

![bayes](https://latex.codecogs.com/svg.latex?P(c|w)=\frac{P(w|c)P(c)}{P(c,w)})

La probabilité a priori de chaque candidat *c* est prise comme la fréquence relative de *c* par rapport aux autres mots du corpus entier, avec lissage de Laplace.   

Pour la probabilité a posteriori que le mot entré soit *w* alors que l’usager ait voulu tapper *c*, nous considérons un modèle basé sur une distribution softmaxée d’une mesure de similarité entre *w* et chaque candidat *c*.
## Mesure de similarité par projection vectorielle fastText
Nous avons examiné en premier lieu une mesure de similarité basée sur une projection des mots dans un espace vectoriel à l'aide de fastText. Le modèle est entraîné sur les 201 315 mots du corpus prétraité voc-1bwc.txt en mode skip-gram en considérant les sous-mots de 2 et 4 caractères. Les candidats retenus pour lesquels nous mesurons la similarité avec *w* sont les 10 plus proches voisins de *w* dans l’espace vectoriel.
![fasttext](https://i.imgur.com/rdvjeLE.png)

Le temps de correction du fichier train.txt ainsi que le poids du modèle croient linéairement avec le nombre de dimensions de l’espace vectoriel alors que le score de qualité stagne à 50% au-delà de 200 dimensions. À 200 dimensions, le modèle fastText atteint un poids faramineux de 1.8 Go. La lourdeur des modèles neuronaux demeure un obstacle à leur déploiement dans les systèmes aux ressources limitées.

## Mesures de similarité entre deux chaînes de caractères


|   | Temps de correction de train.txt | Score de qualité|
| ------------- | ------------- | ------------- |
| Jaro-Winkler  | 27 min  |  65.8%
| Damerau-Levenshtein  | 34 min  | 79.4%
| Levenshtein  | 37 min  | 76.4%

Ces mesures de similarité obtiennent une meilleure performance que le modèle basé sur le plongement vectoriel fastText, au prix d’un temps de correction beaucoup plus long. D’une part, calculer une mesure de similarité entre chaque mot à corriger et chaque mot du corpus est en général ~ *O(m,n)* où *m* est le nombre de mots a corriger et *n* est la taille du corpus. Dans une implémentation naïve de ces algorithmes, chaque instance de calcul est elle-même ~ *O(x,w)* avec *x,w* les tailles des deux mots à comparer. D’autre part, dans un modèle à plongement vectoriel, les voisins les plus proches sont obtenus en calculant la norme euclidienne entre le mot à corriger et chaque mot du corpus. Les implémentations modernes d’opérations matricielles sont beaucoup plus rapides qu’une boucle traditionnelle dans la mesure où elles exploitent le parallélisme des processeurs et permettent le calcul de plusieurs points en un seul appel de fonction. 

Pour éviter d’itérer à travers le corpus en entier et de calculer une mesure de similarité entre chaque mot à corriger et chaque mot du corpus, nous nous attardons à la question de génération d’un sous-ensemble de corrections potentielles à partir d’un mot présumé erroné. Nous générons ces corrections potentielles en deux temps:

1. Nous considérons les altérations qui se trouvent à une unité de distance au sens Levenshtein du mot erroné. Du sous-ensemble de tokens résultants, nous ne retenons que ceux qui apparaissent dans le corpus (i.e. des mots existants). Cette opération coûte ~ *O(m)* dans la mesure où le nombre de mots à corriger est inférieur au nombre de mots dans le corpus.
2. Nous retirons les voyelles de chaque mot du corpus et nous entreposons les tokens résultants dans un dictionnaire *dic_hash = {token: [liste de mots qui ont produit ce token]}*. Cette opération, qui n’est exécutée qu’une seule fois au lancement du programme, peut être vue comme une « mauvaise » fonction de hachage dont nous exploiterons les collisions pour générer des corrections potentielles. Pour corriger un mot, nous le soumettons à la même fonction de hachage, nous le altérons avec l’opération décrite en (1) et nous récupérons les mots du corpus associés aux tokens résultants à l’aide du dictionnaire *dic_hash*. L’ensemble des corrections considérées est l’union de l’ensemble de sortie en (1) et celui-ci.

La vraisemblance de chaque mot candidat généré par cette approche est calculée ensuite calculée à partir d’une ou d’une combinaison linéaire de mesures de similarité dans le domaine des logits.

|   | Temps de correction de train.txt | Score de qualité|
| ------------- | ------------- | ------------- |
| Jaro-Winkler sans hachage  | 18 secondes  |  68.6%
| Double Metaphone sans hachage  | 22 secondes  | 67.6%
| Jaro-Winkler et Double Metaphone sans hachage  | 26 secondes  | 70.0%
| Jaro-Winkler avec hachage | 33 secondes  | 78.6%
| Double Metaphone avec hachage | 58 secondes  | 76.3%
| Jaro-Winkler et Double Metaphone avec hachage  | 72 secondes  | 79.7%

L’approche sélectionnée obtient un score considérablement plus élevé (79.7%) sur train.txt que le modèle basé sur fastText (50.1%) en moins de temps et sans nécessité de stocker de modèles pré-entraînés si ce n’est le dictionnaire de hachage de quelques mégaoctets tout au plus. Nous observons également que les changements proposés en (1) et en (2) rendent le modèle à la fois plus rapide d’au moins 25 fois, et plus performant en termes de qualité, que les implémentations naïves explorées. L’inconvénient de cette approche est la nécessité de prévoir des règles de hachage pour couvrir les autres types d’erreurs d’orthographe, ce qui peut augmenter la complexité du code.

