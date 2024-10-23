import streamlit as st
from pentominoes import ALL_PARTS
from polymino import generate_all, Grid, PENTOMINOES, solutions_svg, unique_grids
from dlx import DLX

st.title("tirthkar kalyanak paheli : LEVEL-2")

# Function to handle level 1
def sortkey(x):
    x = str(x)
    return (len(x), x)

COLOURS = dict(A="#FEF65B", B="#A3FFB4", C="#E1C0B6",
            D="#4974A5", E="#00FFFF", F="#FFA500",
            G="#8D5959", J="#03989E", K="#843C54",
            L="#0000FF", M="#5D782E", H="#FF0000")

# date=[1,2,3,4,5,6,7,8,9,10,11,12,13,14]
# number = st.selectbox("Select Date",date)
# number=int(number)
tithi=[1,2,3,4,5,6,7,8,9,10,11,12,13,14]
tithi_ = st.selectbox("Select tithi",tithi)
tithi_selected=int(tithi_)
if tithi_selected > 0 and  tithi_selected < 8:
    t_row=2
    t_col=tithi_selected-1
if tithi_selected > 7 and  tithi_selected < 15:
    t_row=3
    t_col=tithi_selected-8

mass=["माघ","फाल्गुन","चैत्र","वैशाख","ज्येष्ठ","आषाढ़","श्रावण","भाद्रपद","अश्विन","कार्तिक","मार्गशीर्ष","पौष"]
mass_ = st.selectbox("Select maas",mass)
if mass_==mass[0]:
    m_row=0
    m_col=0
elif mass_==mass[1]:
    m_row=0
    m_col=1
elif mass_==mass[2]:
    m_row=0
    m_col=2
elif mass_==mass[3]:
    m_row=0
    m_col=3
elif mass_==mass[4]:
    m_row=0
    m_col=4
elif mass_==mass[5]:
    m_row=0
    m_col=5
elif mass_==mass[6]:
    m_row=1
    m_col=0
elif mass_==mass[7]:
    m_row=1
    m_col=1
elif mass_==mass[8]:
    m_row=1
    m_col=2
elif mass_==mass[9]:
    m_row=1
    m_col=3
elif mass_==mass[10]:
    m_row=1
    m_col=4
elif mass_==mass[11]:
    m_row=1
    m_col=5

paksha=["अमावस्या","पूर्णिमा","कृष्ण पक्ष","शुक्ल पक्ष"]
paksha_ = st.selectbox("Select paksha",paksha)
if paksha_==paksha[0]:
    p_row=4
    p_col=0
elif paksha_==paksha[1]:
    p_row=4
    p_col=1
elif paksha_==paksha[2]:
    p_row=4
    p_col=2
elif paksha_==paksha[3]:
    p_row=4
    p_col=4

vaar=["सोमवार","मंगलवार","बुधवार","बृहस्पतिवार","शुक्रवार","शनिवार","इतवार"]
vaar_ = st.selectbox("Select vaar",vaar)
if vaar_==vaar[0]:
    v_row=4
    v_col=4
elif vaar_==vaar[1]:
    v_row=4
    v_col=5
elif vaar_==vaar[2]:
    v_row=4
    v_col=6
elif vaar_==vaar[3]:
    v_row=5
    v_col=5
elif vaar_==vaar[4]:
    v_row=5
    v_col=6
elif vaar_==vaar[5]:
    v_row=6
    v_col=5
elif vaar_==vaar[6]:
    v_row=6
    v_col=6


GRID = Grid((7, 7), holes=[(0, 6), (1, 6), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),(t_row, t_col), (m_row, m_col), (p_row, p_col),  (v_row, v_col)])

all_solutions = []  
for PENTOMINOES in ALL_PARTS:
    POLYMINOES = generate_all(PENTOMINOES, GRID)
    POLYMINOES = [polymino.aslist for polymino in POLYMINOES]

    LABELS = list(set([element for polymino in POLYMINOES for element in polymino]))
    LABELS = sorted(LABELS, key=sortkey)
    COVER = DLX(LABELS, POLYMINOES)

    SOLUTIONS = []
    first_solution = True

    for i, SOLUTION in enumerate(COVER.generate_solutions()):
        solution_grid = Grid.from_DLX(SOLUTION)
        if not first_solution:
            solution_grid.flip()
        SOLUTIONS.append(solution_grid)
        if first_solution:
            first_solution = False
            break  

    DISTINCT_SOLUTIONS = unique_grids(SOLUTIONS)
    all_solutions.extend(DISTINCT_SOLUTIONS)  

solutions_svg([all_solutions[0]], filename='first_solution.svg', columns=7, colour=COLOURS.get)
svg_content = open("first_solution.svg", "r").read()
st.image(svg_content, width=2000)
