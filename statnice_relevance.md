# Státnice okruhy × obhajoba bakalářské práce — mapa relevance

Mapování všech **41 okruhů** státní bakalářské zkoušky (KyR, ČVUT FEL 2021, viz
`../../Statnice/index.md`) na obsah obhajobové prezentace `presentation_en.qmd`
(*Trajectory Generation for Redundant Welding Robot with Positioner*).

Práce se dotýká: **kinematiky a inverzní kinematiky robotu, rotační/transformační
algebry, numerické + kombinatorické optimalizace, plánování v konfiguračním prostoru
(RRT-Connect), Jakobiánu/manipulovatelnosti a C++/ROS 2 implementace.**

---

## 🟢 Highly related — komise může navázat přímo z obhajoby

| Okruh | Proč souvisí |
|---|---|
| **6-01 · Kinematika a dynamika robotu a její reprezentace** | Jádro celé práce: IKT2/IKT6, přímá/inverzní kinematika, kaskáda rámců, Jakobián, manipulovatelnost. |
| **6-05 · Stavový prostor a jeho prohledávání** | Plánování ve volném prostoru v 9-DOF konfiguračním prostoru pomocí **OMPL RRT-Connect** (slide *System overview*). |
| **1-02 · Lineární algebra a maticový počet** | Rotační matice, homogenní transformace, „rotace násobena v rámci X", zarovnání podle vektoru gravitace, Jakobián. |
| **1-07 · Optimalizace a matematické programování** | Minimalizace účelové funkce v Ceres, penalizační funkce, metoda nejmenších čtverců + **kombinatorický** výběr větve. |
| **2-01 · Kinematika a dynamika hmotných bodů a tuhých těles** | Fyzikální základ — rotace/transformace tuhého tělesa, na nichž stojí kinematika robotu. |
| **1-04 · Numerická matematika** *(jen numerická část)* | Numerický řešič (Levenberg–Marquardt v Ceres) vs. **uzavřený tvar** analytické IK — doslova jedna z otázek u obhajoby („vysvětlit *closed-form solution*"). Část o diferenciálních rovnicích se neuplatní. |

## 🟡 Medium — částečný překryv, vhodné zopakovat

| Okruh | Proč |
|---|---|
| **5-04 · Linearizace** | Jakobián je linearizace přímé kinematiky; Gauss–Newton / LM linearizuje rezidua. |
| **1-01 · Matematická analýza (více proměnných)** | Gradienty účelové funkce více proměnných řídí optimalizaci. |
| **3-04 · Algoritmy vyhledávání / prohledávání grafů** | Prohledávání plánovacího stromu + výběr větve (blízké RRT, byť to vaše je vzorkovací). |
| **3-01 · Základní programové struktury a techniky** | C++ implementace; otázka *konstanty v době překladu → nutnost rekompilace* (str. 46) patří sem. |
| **1-03 · Teorie grafů** *(jen grafová část)* | RRT je strom; kandidátní větve tvoří malý kombinatorický strom. Logická část se neuplatní. |

## 🟠 Few — jen okrajová vazba

- **1-06 · Pravděpodobnost / náhodné procesy** — RRT-Connect je *náhodný / vzorkovací* plánovač.
- **3-03 · Datové struktury** — stromové struktury za RRT.
- **3-02 · Složitost algoritmů** — složitost plánování/prohledávání.
- **3-06 · Paralelizace** & **3-07 · Synchronizace** — architektura uzlů ROS 2 / meziuzlová komunikace.
- **7-03 · Sítě a protokoly** — ROS 2 / DDS middleware mezi uzly.
- **5-02 · Lineární systémy**, **5-05 · Vzorkování a diskretizace**, **5-07 · Struktura řídicích systémů** — robot jako systém, diskretizovaná/vzorkovaná trajektorie, struktura řídicího systému (v decku nerozvedeno).
- **6-02 · Pohony robotů** — klouby/osy řešíte abstraktně; pohony se neprobírají.
- **2-03 · Fyzikální pole** — pouze vektor gravitace (požadavek na orientaci svaru).
- **2-04 · Termodynamika** — svařovací teplo / tavná lázeň zmíněna jen okrajově.

## ⚪ Not related — bez smysluplného překryvu

1-05 Komplexní analýza & transformace (Fourier/Laplace/Z) · 2-02 Mechanika kontinua ·
2-05 Vlny a optika · 2-06 Moderní fyzika (kvantová/laser/jaderná) · 3-05 Embedded ·
4-01/4-02/4-03 (celá elektronika/digitální technika) · 5-01 Signály/korelace/spektrum ·
5-03 Modely a odezvy · 5-06 Filtry · 5-08 Metody návrhu · 5-09 Neurčitost a robustnost ·
6-03 Statistické rozhodování · 6-04 Klasifikátory · 6-06 Hry · 7-01 Senzory a měření ·
7-02 Teorie informace a kódování.

---

**Shrnutí pro přípravu na obhajobu:** komise může nejpřirozeněji navázat z okruhů
**6-01, 6-05, 1-02, 1-07, 2-01 a numerické části 1-04** — těchto šest je tam, kde se
práce a státnicový sylabus skutečně překrývají.
