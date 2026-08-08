# Method

Executable components for the **aibusiness.vc × NeoMundi test-purchase and runtime receipt-conformity pilot**.

[🇫🇷 Lire en français](#version-française)

---

# English

## What is this folder for?

This folder contains the small set of tools used to **run the method**.

If `docs/` is the instruction book, then `method/` is the toolbox.

**In simple terms:**

> **`docs/` explains what we want to test.  
> `method/` contains the tools that run the test.  
> `evidence/` contains what happened when the test was run.**

The method is intentionally separated from the evidence so that someone can inspect the logic without confusing the code with the results it produced.

---

## Structure

    method/
    ├── README.md
    ├── simulator.py
    ├── harness.py
    ├── validate_receipt.py
    └── prompts/
        ├── ai_policy.txt
        ├── service_passport.txt
        ├── receipt_template.txt
        ├── service_agent.txt
        ├── buyer.txt
        └── analyst.txt

Exact filenames may follow the original source package where needed.

---

## The method in one sentence

> **Create a controlled AI service interaction, record what the platform actually executes, generate an AI receipt, then compare that receipt deterministically with the authoritative execution evidence.**

NeoMundi comes afterward as an independent runtime measurement and trace layer.

---

## How it works

At a high level:

    Prompts + declared service rules
                 ↓
          AI buyer / service agent
                 ↓
              harness
                 ↓
             simulator
                 ↓
       authoritative journal + state
                 ↓
          AI-generated receipt
                 ↓
       deterministic validator
                 ↓
        receipt-conformity result
                 ↓
         NeoMundi observation
                 ↓
            trace / evidence

The key idea is simple:

**the AI's own receipt is not the source of truth.**

The source of truth for executed operations is the platform evidence produced during the run.

---

## Components

### `simulator.py`

The simulator represents the controlled service environment.

Its job is to expose the operations that the AI service agent can use and to preserve what actually happened during execution.

Depending on the run, the simulator can contribute to artifacts such as:

- execution events;
- final platform state;
- timestamps;
- event identifiers;
- journal entries.

Think of it as the **little world in which the agent acts**.

---

### `harness.py`

The harness orchestrates the experiment.

It coordinates the different roles and components needed for a run.

At a high level, it connects:

- the controlled scenario;
- the AI buyer;
- the AI service agent;
- the simulator;
- the generation of runtime artifacts.

Think of it as the **conductor of the experiment**.

The harness should not decide whether the receipt is conformant.

That responsibility belongs to the deterministic validator.

---

### `validate_receipt.py`

The deterministic validator compares the AI-generated receipt with the authoritative run evidence.

Reference validator:

`receipt_vs_journal 1.1`

It can inspect elements such as:

- executed events;
- material actions declared in the receipt;
- relevant values recorded in the journal;
- final state;
- journal integrity;
- missing or divergent information.

It produces a structured validation result including concepts such as:

- `receipt_conformity`;
- `journal_integrity`;
- delta count;
- delta severity;
- policy advisory.

**This is the component that determines receipt conformity in this pilot.**

NeoMundi does not replace this validator.

---

## Prompts

The `prompts/` directory contains the declared instructions used for the AI roles and service framework.

### `ai_policy.txt`

Defines the policy context supplied to the experiment.

### `service_passport.txt`

Describes the declared service and its expected operating context.

### `receipt_template.txt`

Defines the expected structure or instructions for the AI-generated receipt.

### `service_agent.txt`

Instructions for the AI acting as the service agent.

### `buyer.txt`

Instructions for the AI acting as the test buyer / mystery shopper.

### `analyst.txt`

Instructions for the optional qualitative analyst role.

The prompts are preserved because changing a prompt can change the experiment.

They are therefore part of the reproducibility context.

---

## Authoritative evidence vs AI self-report

The method deliberately distinguishes two categories.

### AI self-report

Examples:

- the generated receipt;
- statements made by the service agent;
- explanations produced by an AI.

These can be useful, but they are not authoritative simply because the model produced them.

### Authoritative execution evidence

Examples:

- the append-only execution journal;
- recorded tool operations;
- final platform state;
- frozen run artifacts.

These are used as the reference for deterministic receipt comparison.

The method therefore asks:

> **Does what the AI says it did match what the system recorded that it actually did?**

---

## Deterministic validation

The conformity check is designed to be deterministic.

That means the same frozen receipt and the same frozen authoritative evidence should produce the same validation result under the same validator and policy versions.

This is important because the conformity result should not depend on asking another AI model to “judge” the receipt differently each time.

A qualitative AI analysis may exist as a separate layer, but it is not the authoritative receipt-conformity mechanism.

---

## Policy is separate from evidence

The validator measures differences.

A versioned policy interprets those differences.

For example:

| Measured condition | Conformity | Advisory |
|---|---|---|
| No delta, intact journal | `conformant` | `none` |
| Minor delta(s) | `conformant_with_deviations` | `notice` |
| Major delta | `conformant_with_deviations` | `review_recommended` |
| Critical delta | `non_conformant` | `not_reliable` |
| Broken journal integrity | `non_conformant` | `not_reliable` |

This distinction matters:

**evidence can stay frozen while interpretation policy evolves.**

---

## Relationship with NeoMundi

After deterministic validation, the resulting observation can be submitted to NeoMundi ControlTower.

In the reference pilot, the NeoMundi bridge uses:

`mode = OBS`

NeoMundi provides:

- runtime measurement;
- measurement-layer classification;
- request ID;
- trace ID;
- versioned measurement information.

NeoMundi does **not** become the native receipt-conformity authority.

In particular:

> **ControlTower `ALLOW` does not mean that a receipt is conformant.**

The clean / failing acceptance pair in this pilot is useful precisely because deterministic receipt conformity changes while the ControlTower measurement remains the same.

---

## Reproducibility principles

A reproducible run should preserve, where applicable:

- the exact prompt versions;
- scenario and service versions;
- simulator version;
- harness version;
- validator version;
- conformity-policy version;
- model designations;
- frozen transcript;
- authoritative journal;
- final state;
- generated receipt;
- validation report;
- NeoMundi request and response;
- controlled mutations, if any.

A deliberate defect must be documented rather than silently introduced.

---

## What this folder does not contain

`method/` should not be used as the main storage location for completed run evidence.

Completed run artifacts belong in `evidence/`.

This folder should also not contain:

- API keys;
- private credentials;
- production secrets;
- personal data that is unnecessary for reproduction.

Configuration examples should use placeholders for secrets.

---

## Current scope

The method demonstrates a controlled reference implementation for:

- AI-agent test purchase;
- simulated service execution;
- authoritative event recording;
- AI receipt generation;
- deterministic receipt-versus-journal validation;
- versioned conformity interpretation;
- NeoMundi runtime observation.

It is not presented as a universal agent-governance framework or a production-ready service.

---

# Version française

[🇬🇧 Back to English](#english)

## À quoi sert ce dossier ?

Ce dossier contient le petit ensemble d’outils utilisés pour **exécuter la méthode**.

Si `docs/` est le mode d’emploi, alors `method/` est la boîte à outils.

**En termes simples :**

> **`docs/` explique ce que nous voulons tester.  
> `method/` contient les outils qui exécutent le test.  
> `evidence/` contient ce qui s’est réellement passé lorsque le test a été exécuté.**

La méthode est volontairement séparée des preuves afin que l’on puisse examiner la logique sans confondre le code avec les résultats qu’il produit.

---

## Structure

    method/
    ├── README.md
    ├── simulator.py
    ├── harness.py
    ├── validate_receipt.py
    └── prompts/
        ├── ai_policy.txt
        ├── service_passport.txt
        ├── receipt_template.txt
        ├── service_agent.txt
        ├── buyer.txt
        └── analyst.txt

Les noms exacts des fichiers peuvent conserver ceux du package source lorsque cela est nécessaire.

---

## La méthode en une phrase

> **Créer une interaction de service IA contrôlée, enregistrer ce que la plateforme exécute réellement, générer un reçu IA, puis comparer ce reçu de manière déterministe avec les preuves d’exécution autoritatives.**

NeoMundi intervient ensuite comme couche indépendante de mesure runtime et de trace.

---

## Comment cela fonctionne

À haut niveau :

    Prompts + règles de service déclarées
                  ↓
        Acheteur IA / agent de service
                  ↓
               harness
                  ↓
              simulator
                  ↓
        journal autoritatif + état
                  ↓
             reçu généré par l’IA
                  ↓
        validateur déterministe
                  ↓
          résultat de conformité
                  ↓
          observation NeoMundi
                  ↓
             trace / preuve

L’idée centrale est simple :

**le reçu produit par l’IA n’est pas lui-même la source de vérité.**

La référence pour les opérations exécutées est constituée par les preuves de plateforme produites pendant le run.

---

## Composants

### `simulator.py`

Le simulateur représente l’environnement de service contrôlé.

Son rôle est d’exposer les opérations utilisables par l’agent IA de service et de conserver ce qui s’est réellement passé pendant l’exécution.

Selon le run, le simulateur peut contribuer à des artefacts tels que :

- événements d’exécution ;
- état final de la plateforme ;
- horodatages ;
- identifiants d’événements ;
- entrées du journal.

On peut le voir comme le **petit monde dans lequel l’agent agit**.

---

### `harness.py`

Le harness orchestre l’expérience.

Il coordonne les différents rôles et composants nécessaires à un run.

À haut niveau, il relie :

- le scénario contrôlé ;
- l’acheteur IA ;
- l’agent IA de service ;
- le simulateur ;
- la génération des artefacts runtime.

On peut le voir comme le **chef d’orchestre de l’expérience**.

Le harness ne doit pas décider si le reçu est conforme.

Cette responsabilité appartient au validateur déterministe.

---

### `validate_receipt.py`

Le validateur déterministe compare le reçu généré par l’IA avec les preuves autoritatives du run.

Validateur de référence :

`receipt_vs_journal 1.1`

Il peut contrôler notamment :

- les événements exécutés ;
- les actions matérielles déclarées dans le reçu ;
- les valeurs pertinentes enregistrées dans le journal ;
- l’état final ;
- l’intégrité du journal ;
- les informations absentes ou divergentes.

Il produit un résultat de validation structuré avec notamment :

- `receipt_conformity` ;
- `journal_integrity` ;
- nombre d’écarts ;
- sévérité des écarts ;
- advisory de politique.

**C’est ce composant qui détermine la conformité du reçu dans ce pilote.**

NeoMundi ne remplace pas ce validateur.

---

## Prompts

Le dossier `prompts/` contient les instructions déclarées utilisées pour les rôles IA et le cadre de service.

### `ai_policy.txt`

Définit le contexte de politique fourni à l’expérience.

### `service_passport.txt`

Décrit le service déclaré et son contexte d’exécution attendu.

### `receipt_template.txt`

Définit la structure ou les instructions attendues pour le reçu généré par l’IA.

### `service_agent.txt`

Instructions de l’IA jouant le rôle d’agent de service.

### `buyer.txt`

Instructions de l’IA jouant le rôle d’acheteur test / mystery shopper.

### `analyst.txt`

Instructions du rôle optionnel d’analyste qualitatif.

Les prompts sont conservés parce qu’une modification de prompt peut modifier l’expérience.

Ils font donc partie du contexte de reproductibilité.

---

## Preuve autoritative vs auto-déclaration IA

La méthode distingue volontairement deux catégories.

### Auto-déclaration IA

Exemples :

- le reçu généré ;
- les déclarations de l’agent de service ;
- les explications produites par une IA.

Ces éléments peuvent être utiles, mais ils ne deviennent pas autoritatifs simplement parce qu’un modèle les a produits.

### Preuves d’exécution autoritatives

Exemples :

- journal d’exécution append-only ;
- opérations outils enregistrées ;
- état final de la plateforme ;
- artefacts gelés du run.

Elles servent de référence pour la comparaison déterministe du reçu.

La méthode pose donc la question :

> **Ce que l’IA dit avoir fait correspond-il à ce que le système a enregistré comme ayant réellement été exécuté ?**

---

## Validation déterministe

Le contrôle de conformité est conçu pour être déterministe.

Cela signifie que le même reçu gelé et les mêmes preuves autoritatives gelées doivent produire le même résultat de validation avec les mêmes versions du validateur et de la politique.

C’est important car le résultat de conformité ne doit pas dépendre du fait de demander à un autre modèle IA de « juger » différemment le reçu à chaque exécution.

Une analyse qualitative par IA peut exister comme couche séparée, mais elle ne constitue pas le mécanisme autoritatif de conformité du reçu.

---

## La politique est séparée des preuves

Le validateur mesure les écarts.

Une politique versionnée interprète ces écarts.

Par exemple :

| Condition mesurée | Conformité | Advisory |
|---|---|---|
| Aucun écart, journal intact | `conformant` | `none` |
| Écart(s) mineur(s) | `conformant_with_deviations` | `notice` |
| Écart majeur | `conformant_with_deviations` | `review_recommended` |
| Écart critique | `non_conformant` | `not_reliable` |
| Intégrité du journal rompue | `non_conformant` | `not_reliable` |

Cette distinction est importante :

**les preuves peuvent rester gelées tandis que la politique d’interprétation évolue.**

---

## Relation avec NeoMundi

Après validation déterministe, l’observation résultante peut être envoyée à NeoMundi ControlTower.

Dans le pilote de référence, le bridge NeoMundi utilise :

`mode = OBS`

NeoMundi fournit :

- une mesure runtime ;
- une classification de couche de mesure ;
- un request ID ;
- un trace ID ;
- des informations de mesure versionnées.

NeoMundi ne devient **pas** l’autorité native de conformité du reçu.

En particulier :

> **Un `ALLOW` ControlTower ne signifie pas qu’un reçu est conforme.**

La paire d’acceptation propre / défaillante du pilote est précisément utile parce que la conformité déterministe change tandis que la mesure ControlTower reste identique.

---

## Principes de reproductibilité

Un run reproductible doit conserver, lorsque cela s’applique :

- les versions exactes des prompts ;
- les versions du scénario et du service ;
- la version du simulateur ;
- la version du harness ;
- la version du validateur ;
- la version de la politique de conformité ;
- les désignations des modèles ;
- le transcript gelé ;
- le journal autoritatif ;
- l’état final ;
- le reçu généré ;
- le rapport de validation ;
- la requête et la réponse NeoMundi ;
- les mutations contrôlées éventuelles.

Un défaut volontaire doit être documenté et non introduit silencieusement.

---

## Ce que ce dossier ne contient pas

`method/` ne doit pas servir de dossier principal pour les preuves des runs terminés.

Les artefacts des runs terminés appartiennent à `evidence/`.

Ce dossier ne doit pas non plus contenir :

- clés API ;
- identifiants privés ;
- secrets de production ;
- données personnelles inutiles à la reproductibilité.

Les exemples de configuration doivent utiliser des placeholders pour les secrets.

---

## Périmètre actuel

La méthode démontre une implémentation contrôlée de référence pour :

- test-purchase d’agent IA ;
- exécution simulée d’un service ;
- enregistrement autoritatif des événements ;
- génération d’un reçu IA ;
- validation déterministe reçu-versus-journal ;
- interprétation de conformité versionnée ;
- observation runtime NeoMundi.

Elle n’est pas présentée comme un framework universel de gouvernance des agents ni comme un service prêt pour la production.
