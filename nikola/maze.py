import random
import queue
import os
import time
import urllib.request 
from tqdm import tqdm
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from graphviz import Graph
from PIL import Image
import webbrowser

"""
Priprema modula za korištenje

Prilikom importa modula 'maze', poziva se ova metoda, koja kreira folder 'maze', a unutar njega podfoldere:
    'maze_parts' - folder koji sadrži potrebne sličice za generiranje slike labirinta (slike se odmah preuzimaju sa sljedeće lokacije:
                    'https://github.com/alen-kl/dstgLabirint/blob/master/maze_images/{naziv_slike}?raw=true')
    'mazes_txt' - folder koji sadrži tekstualnu reprezentaciju generiranog labirinta; način obilježavanja dan je sljedećom tablicom:
                  simbol predstavlja manju sličicu koja se umeće na odgovovarajuće mjesto u slici prilikom generiranja labirinta, npr.
                  slovo f - simbol predstavlja da taj element slike labirinta ima zidove na lijevoj i gornjoj strani
                  
                  slovo | simbol
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  a     | prazno
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  b     | |
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  c     | ¯
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  d     |  |
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  e     | _
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  f     | |¯
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  g     | ¯|
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  h     | _|
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  i     | |_
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  j     | | |
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  k     | =
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  l     | |¯|
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  m     | =|
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  n     | |_|
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  o     | |=
                  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                  p     | |=|
                  
                  Modul omogućuje i kreiranje nove ili izmjene postojeće datoteke, odnosno umjesto generianja, čitanje iz datoteke, gdje se
                  mogu priložiti vlastiti 'labirinti'
    'temp' - folder u koji se pohranjuju sve generirane slike labirinta, njegovog rješenja i stabla s obzirom na početak
    

Parameters
----------

Returns
-------
"""
def _prepare_module():
    print ("Creating necessary folders ...")
    _createFolder('maze/maze_parts')
    _createFolder('maze/temp')
    _createFolder('maze/mazes_txt')
    names = [f'{i}.png' for i in range(1,7)]
    names.extend(['krajevi_hor.png', 'krajevi_ver.png', 'ravno_hor.png', 'ravno_ver.png', 'kut.png', 'beg.png', 'end.png'])
    print ("Downloading required images ...")
    for i in tqdm(range(len(names))):
        if not os.path.exists(f'maze/maze_parts/{names[i]}'):
            urllib.request.urlretrieve(f'https://github.com/alen-kl/dstgLabirint/blob/master/maze_images/{names[i]}?raw=true',
                                       f'maze/maze_parts/{names[i]}')
    print ("Finished downloading images!")

"""
Kreiranje novog foldera na temelju trenutne lokacije učitavanja modula


Parameters
----------
name
    novo ime foldera

Returns
-------
"""
def _createFolder(name):
    path = os.path.join(os.getcwd(), name)
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print ('Error: Creating directory. ' +  name)

"""
Brisanje svih datoteka koje završavaju sa zadanom ekstenzijom na temelju trenutne lokacije učitavanja modula


Parameters
----------
path
    folder trenutne lokacije učitavanja modula
ext
    ciljana ekstenzija
    
Returns
-------
"""
def _deleteFiles(path, ext):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.' + ext):
                os.remove(os.path.join(root, file))
        
"""
Generiranje novog labirinta

Ova funkcija koristi interne strukture i funkcije (detaljnije objašnjeno u samoj razradi teme) za generiranje novog labirinta. 


Parameters
----------
brojRedaka
    broj redova novog labirinta
brojStupaca
    broj stupaca novog labirinta
maze_name
    ime novog labirinta, koje će biti iskorišteno prilikom geneiranja teksutalne reprezentacije labirinta i stabla
open_in
    ukoliko je vrijednost 'browser', slika stabla biti će prikazana u odgovarajućem programu nakon što se završi njeno generiranje
    (kod velikih labirinata to može potrajati do nekoliko minuta)
  
Returns
-------
koord
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista tupleova
    koordinata susjeda ključa
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
(n1, n2, n3)
    n1 - uređeni par koji predstavlja koordinate početka, odnosno ulaza u labirint
    n2 - uređeni par koji predstavlja koordinate kraja, no ne i nužno izlaza iz labirinta, već može kraj biti i negdje unutra
    n3 - uređeni par koji predstavlja koordinate kraja, odnosno izlaza iz labirinta (obavezno uz rub)
"""        
def generate_maze(brojRedaka, brojStupaca, maze_name, open_in='browser'):
    class Celija:
        def __init__(self, x, y, posjeceno):
            self.koordinate=(x,y)
            self.posjeceno = posjeceno
            self.susjedi=[]
            self.s=[]
            self.children=[]
            self.razina=0

    class cell:
        def __init__(self,koordinate,broj):
            self.koordinate=koordinate
            self.broj=broj
            
    def generirajCelije(x,y,lista):
        for i in range (0,x):
            for j in range (0,y):
                lista.append(Celija(i,j,False))

    def popuniSusjede1(lista):
        for c in range(0,brojRedaka*brojStupaca):
            if(c==0):
                lista[c].susjedi.append(1)
                lista[c].susjedi.append(brojStupaca)
            elif(c==brojStupaca-1):
                lista[c].susjedi.append(c-1)
                lista[c].susjedi.append(c+brojStupaca)
            elif(c==brojStupaca*(brojRedaka-1)):
                lista[c].susjedi.append(c-brojStupaca)
                lista[c].susjedi.append(c+1)
            elif(c==brojRedaka*brojStupaca-1):
                lista[c].susjedi.append(c-brojStupaca)
                lista[c].susjedi.append(c-1)
            elif(c in range (1,brojStupaca-1)):
                lista[c].susjedi.append(c+1)
                lista[c].susjedi.append(c-1)
                lista[c].susjedi.append(c+brojStupaca)
            elif(c%brojStupaca==0 and c!=0 and c!=brojStupaca*(brojRedaka-1)):
                lista[c].susjedi.append(c+1)
                lista[c].susjedi.append(c+brojStupaca)
                lista[c].susjedi.append(c-brojStupaca)
            elif(c%brojStupaca==brojStupaca-1 and c!=brojStupaca-1 and c!=brojRedaka*brojStupaca-1):
                lista[c].susjedi.append(c-1)
                lista[c].susjedi.append(c-brojStupaca)
                lista[c].susjedi.append(c+brojStupaca)
            elif(c in range (brojStupaca*(brojRedaka-1)+1,brojRedaka*brojStupaca-1)):
                lista[c].susjedi.append(c-1)
                lista[c].susjedi.append(c+1)
                lista[c].susjedi.append(c-brojStupaca)
            else:
                lista[c].susjedi.append(c+1)
                lista[c].susjedi.append(c-1)
                lista[c].susjedi.append(c+brojStupaca)
                lista[c].susjedi.append(c-brojStupaca)

    def randomN(redak,stupac):
        svi=[]
        x = (stupac-1)*[0] + list(range(redak)) + (stupac-1)*[redak-1] + list(range(redak-1))[:0:-1]
        y = list(range(stupac)) + (redak-1)*[stupac-1] + list(range(stupac-1))[:0:-1] + (redak-1)*[0]
        for i,j in zip(x,y):
            svi.append(i*stupac + j)
        return random.choice(svi)
    ##########################
    
    red=queue.Queue()
    listaCelija1=[];

    generirajCelije(brojRedaka,brojStupaca,listaCelija1)
    popuniSusjede1(listaCelija1)

    #+++++++++++++++++++++++++++++++++++++++++++++++#
    #1
    n = randomN(brojRedaka,brojStupaca)
    listaCelija1[n].razina=0
    korijen=listaCelija1[n].koordinate

    while(1):
        #3
        listaCelija1[n].posjeceno=True

        #2
        c=cell(listaCelija1[n].koordinate,n)
        red.put(c)
        #4
        neposjeceniSusjediCelije=[]
        for el in listaCelija1[n].susjedi:
            if(listaCelija1[el].posjeceno==False):
                neposjeceniSusjediCelije.append(el)
        if(len(neposjeceniSusjediCelije)==0):
            while(red.empty()==False):
                celija=red.get()
                n=celija.broj
                for elem in listaCelija1[n].susjedi:
                    if(listaCelija1[elem].posjeceno==False):
                        neposjeceniSusjediCelije.append(elem)
                if(len(neposjeceniSusjediCelije)!=0):
                    break
                    
        if(len(neposjeceniSusjediCelije)==0):
            break
        a=random.choice(neposjeceniSusjediCelije)

        #5
        listaCelija1[a].s.append(listaCelija1[n].koordinate)
        listaCelija1[n].s.append(listaCelija1[a].koordinate)
        
        listaCelija1[n].children.append(listaCelija1[a].koordinate)
        listaCelija1[a].razina=listaCelija1[n].razina+1

        #6
        n=a

        #7 petlja
    #+++++++++++++++++++++++++++++++++++++++++++++++#

    def vratiKrajeve(lista):
        krajevi=[]
        maxRazina=0
        for celija in lista:
            if celija.razina>maxRazina:
                maxRazina=celija.razina

        for celija in lista:
            if(celija.razina==maxRazina):
                krajevi.append(celija.koordinate)
        return krajevi
    
    def vratiRubne(redak,stupac):
        svi=[]
        rubni=[]
        x = (stupac-1)*[0] + list(range(redak)) + (stupac-1)*[redak-1] + list(range(redak-1))[:0:-1]
        y = list(range(stupac)) + (redak-1)*[stupac-1] + list(range(stupac-1))[:0:-1] + (redak-1)*[0]
        for i,j in zip(x,y):
            svi.append(i*stupac + j)
        for r in svi:
            rubni.append(listaCelija1[r])
        return rubni    

    krajevi=vratiKrajeve(listaCelija1)
    krajeviNaRubu=vratiKrajeve(vratiRubne(brojRedaka,brojStupaca))
    
    koord = {}
    for item in listaCelija1:
        koord[item.koordinate] = item.s

    #crtanje grafa#
    
    listaCelija1.sort(key = lambda item: item.razina)
    g = Graph(format='png')
    
    for node in listaCelija1:
        g.node(str(node.koordinate[0]*brojStupaca+node.koordinate[1]), str(node.koordinate))
        
    for node in listaCelija1:
        for i in koord[node.koordinate]:
            g.edge(str(node.koordinate[0]*brojStupaca+node.koordinate[1]), str(i[0]*brojStupaca+i[1]))
            
    print ("\nThis may take a while ...")
    save_name = f"maze/temp/{maze_name}"
    if open_in == 'browser':
        g.render(save_name + '_stablo.gv', view=True)
    else:
        g.render(save_name + '_stablo.gv')
    
    print ("\nFinally done!")
    maze = _get_letters(koord, brojRedaka, brojStupaca)
    _save_maze(maze, maze_name)
    _deleteFiles(os.getcwd(), 'gv')
    return koord, maze, (korijen, krajevi.pop(), krajeviNaRubu.pop())

"""
Učitavanje labirinta iz njegove tekstualne reprezentacije iz 'maze/mazes_txt' foldera


Parameters
----------
maze_name
    ime datoteke željenog labirinta

Returns
-------
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
"""
def read_maze(maze_name):
    return [[i for i in line.rstrip('\n')] for line in open(f'maze/mazes_txt/{maze_name}.txt')]

"""
Pohranjivanje labirinta u njegovu tekstualnu reprezentacije u 'maze/mazes_txt' folder


Parameters
----------
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
maze_name
    ime datoteke željenog labirinta

Returns
-------
"""
def _save_maze(maze, maze_name):
    with open(f'maze/mazes_txt/{maze_name}.txt', 'w') as file:
        for row in maze:
            file.write(''.join(row) + '\n')

"""
Generiranje 2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje) iz
koordinata (koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista
tupleova koordinata susjeda ključa)

    Prilikom generiranja slova, iz perspektive samog elementa, korištene su sljedeće oznake:

    strana | oznaka
    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    lijevo | W(est)
    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    gore   | N(orth)
    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    desno  | E(ast)
    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    dolje  | S(outh)
    
    Ove oznake će se pojavljivati i kasnije kroz implementaciju, pa se korisnik može ovdje referencirati 
    
Parameters
----------
koordinate
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista
    tupleova koordinata susjeda ključa
redak
    broj redaka labirinta
stupac
    broj stupaca labirinta
    
Returns
-------
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
"""
def _get_letters(koordinate, redak, stupac):
    maze = [['' for j in range(stupac)] for i in range(redak)]
    for key, value in koordinate.items():
        x,y = key
        sides = 'NESW'
        for k, v in value:
            if x == k and y < v:
                sides = sides.replace('E', '')
            elif x == k and y > v:
                sides = sides.replace('W', '')
            elif x < k and y == v:
                sides = sides.replace('S', '')
            elif x > k and y == v:
                sides = sides.replace('N','')
        if sides == '':
            maze[x][y] = 'a'
        elif sides == 'W':
            maze[x][y] = 'b'
        elif sides == 'N':
            maze[x][y] = 'c'
        elif sides =='E':
            maze[x][y] = 'd'
        elif sides == 'S':
            maze[x][y] = 'e'
        elif sides == 'NW':
            maze[x][y] = 'f'
        elif sides == 'NE':
            maze[x][y] = 'g'
        elif sides == 'ES':
            maze[x][y] = 'h'
        elif sides == 'SW':
            maze[x][y] = 'i'
        elif sides == 'EW':
            maze[x][y] = 'j'
        elif sides == 'NS':
            maze[x][y] = 'k'
        elif sides == 'NEW':
            maze[x][y] = 'l'
        elif sides == 'NES':
            maze[x][y] = 'm'
        elif sides == 'ESW':
            maze[x][y] = 'n'
        elif sides == 'NSW':
            maze[x][y] = 'o'
        elif sides == 'NESW':
            maze[x][y] = 'p'
    return maze

"""
Pretraživanje i odabir (po potrebi rotacija) potrebne slike za potrebe generiranja slike labirinta iz 'maze/maze_parts' foldera

Parameters
----------
images
    lista objekata klase Image iz PIL-a - potrebne slike
y
    slovo za element

Returns
-------
image
    potrebna (modificirana) slika
"""
def _find_image(images, y):
    if y == 'a':
        return images[0]
    elif y == 'b':
        return images[1]
    elif y == 'c':
        return images[1].rotate(270)
    elif y == 'd':
        return images[1].rotate(180)
    elif y == 'e':
        return images[1].rotate(90)
    elif y == 'f':
        return images[2]
    elif y == 'g':
        return images[2].rotate(270)
    elif y == 'h':
        return images[2].rotate(180)
    elif y == 'i':
        return images[2].rotate(90)
    elif y == 'j':
        return images[3]
    elif y == 'k':
        return images[3].rotate(90)
    elif y == 'l':
        return images[4]
    elif y == 'm':
        return images[4].rotate(270)
    elif y == 'n':
        return images[4].rotate(180)
    elif y == 'o':
        return images[4].rotate(90)
    elif y == 'p':
        return images[5]

"""
Kreiranje slike labirinta iz 2d polja, čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)

Funkcija kreira i druge moguće reprezentacije pohrane stabla, odnosno grafa iz tog 2d polja.
Nakon što završi s kreiranjem slike, pohranjena slika se prikazuje u odgovarajućem programu za pregled.

Parameters
----------
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
row
    broj redaka labirinta
column
    broj stupaca labirinta
maze_name
    ime labirinta koje će se iskoristiti za ime slike labirinta
open_in
    ukoliko je vrijednost 'browser', slika stabla biti će prikazana u odgovarajućem programu nakon što se završi njeno generiranje
    (kod velikih labirinata to može potrajati do nekoliko minuta)
    
Returns
-------
image
    nova slika koja je objekt klase Image iz PIL-a
koordinate
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista tupleova
    koordinata susjeda ključa
susjed
    matrica susjedstva stabla u obliku 2d polja s vrijednostima 0 ili 1
matrix
    2d polje koje za element sadrži rječnik s ključevima 'W', 'N', 'E' i 'S' (prethodno objašnjeno kod generiranja 2d polja slova),
    a za vrijednost imaju ili 0, ako s te odgovorajuće strane nemaju susjeda, odnosno sam element iz tog polja, ako na toj stani imaju
    susjeda
"""    
def create_maze(maze, row, column, maze_name, open_in='browser'):
    koordinate = {}
    open_images = []
    matrix = [[{'S':0, 'N':0, 'E':0, 'W':0} for j in range(column)] for i in range(row)]
    susjed = [[0 for j in range(row*column)] for i in range(row*column)]
    for i in range(1, 7):
        open_images.append(Image.open(f'maze/maze_parts/{i}.png'))
    width, height = open_images[0].size
    blank_image = Image.new("RGB", (width*column, height*row))
    for (i, x) in enumerate(maze):
        h = height * i
        for (j, y) in enumerate(x):
            w = width * j
            if y == 'a':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i-1,j), (i,j+1), (i+1,j), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'b':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                koordinate[(i,j)] = [(i-1,j), (i,j+1), (i+1,j)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'c':
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i,j+1), (i+1,j), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'd':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i-1,j), (i+1,j), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'e':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i-1,j), (i,j+1), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'f':
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                koordinate[(i,j)] = [(i,j+1), (i+1,j)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'g':
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i+1,j), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'h':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i-1,j), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'i':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                koordinate[(i,j)] = [(i-1,j), (i,j+1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'j':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                koordinate[(i,j)] = [(i-1,j), (i+1,j)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'k':
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i,j+1), (i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'l':
                if i < row - 1:
                    matrix[i][j]['S'] = matrix[i+1][j]
                    susjed[i*column+j][(i+1)*column+j] = 1
                koordinate[(i,j)] = [(i+1,j)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'm':
                if j > 0:
                    matrix[i][j]['W'] = matrix[i][j-1]
                    susjed[i*column+j][i*column+(j-1)] = 1
                koordinate[(i,j)] = [(i,j-1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'n':
                if i > 0:
                    matrix[i][j]['N'] = matrix[i-1][j]
                    susjed[i*column+j][(i-1)*column+j] = 1
                koordinate[(i,j)] = [(i-1,j)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'o':
                if j < column - 1:
                    matrix[i][j]['E'] = matrix[i][j+1]
                    susjed[i*column+j][i*column+(j+1)] = 1
                koordinate[(i,j)] = [(i,j+1)]
                blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'p':
                blank_image.paste(_find_image(open_images, y), (w, h))
    for i in range(6):
        open_images[i].close()
    save_name = f'maze/temp/{time.strftime("%Y%m%d_%H%M%S")}_{maze_name}.jpg'
    blank_image.save(save_name)
    if open_in == 'browser':
        webbrowser.open('file://' + os.getcwd() + '/' + save_name)
    return blank_image, koordinate, susjed, matrix

"""
Modificirani DFS algoritam za pretraživanje svih mogućih putova između dva vrha grafa

Algoritam se temelji na DFS algoritmu, ali je proširen da na temelju strukture podataka grafa (koordinate susjedstva novog labirinta,
odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista tupleova koordinata susjeda ključa) određuje sve
moguće putove između zadanog početka i cilja (naravno, da će u ovom slučaju algoritam uvijek vratiti samo jedan put, jer u stablu između
svaka dva vrha postoji jedinstven put). Algoritam je napisan u obliku generatora koji vraća moguće putove. Algoritam je detaljnije opisan
u samoj izradi.

Parameters
----------
graf
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost
    lista tupleova koordinata susjeda ključa
pocetak
    uređen par koji je koordinata početka traženja (kod labirinta ulaz)
kraj
    uređen par koji je koordinata kraja traženja (kod labirinta izlaz)
    
Returns
-------
put
    lista uređenih parova koji su koordinate traženog puta između 'pocetak' i 'kraj'
"""
def _dfs_paths(graf, pocetak, kraj):
    stog = [(pocetak, [pocetak])]
    while stog:
        (vrh, put) = stog.pop()
        for sljed in [x for x in graf[vrh] if x not in put]:
            if sljed == kraj:
                yield put + [sljed]
            else:
                stog.append((sljed, put + [sljed]))

"""
Modificirani BFS algoritam za pretraživanje svih mogućih putova između dva vrha grafa

Algoritam se temelji na BFS algoritmu, ali je proširen da na temelju strukture podataka grafa (koordinate susjedstva novog labirinta,
odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost lista tupleova koordinata susjeda ključa) određuje sve
moguće putove između zadanog početka i cilja (naravno, da će u ovom slučaju algoritam uvijek vratiti samo jedan put, jer u stablu između
svaka dva vrha postoji jedinstven put). Algoritam je napisan u obliku generatora koji vraća moguće putove. Algoritam je detaljnije opisan
u samoj izradi.

Parameters
----------
graf
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost
    lista tupleova koordinata susjeda ključa
pocetak
    uređen par koji je koordinata početka traženja (kod labirinta ulaz)
kraj
    uređen par koji je koordinata kraja traženja (kod labirinta izlaz)
    
Returns
-------
put
    lista uređenih parova koji su koordinate traženog puta između 'pocetak' i 'kraj'
"""                
def _bfs_paths(graf, pocetak, kraj):
    red = [(pocetak, [pocetak])]
    while red:
        (vrh, put) = red.pop(0)
        for sljed in [x for x in graf[vrh] if x not in put]:
            if sljed == kraj:
                yield put + [sljed]
            else:
                red.append((sljed, put + [sljed]))

"""
Funkcija koja obuhvaća pozive prethodnih metoda '_dfs_paths' i '_bfs_paths' te vraća jednu lista uređenih parova, koji su koordinate
traženog puta (ako ih ima više, vraća najdulji od puteva)

Parameters
----------
koordinate
    koordinate susjedstva novog labirinta, odnosno stabla - rječnik čiji je ključ tuple koordinata vrha, a vrijednost
    lista tupleova koordinata susjeda ključa
start
    uređen par koji je koordinata početka traženja (kod labirinta ulaz)
goal
    uređen par koji je koordinata kraja traženja (kod labirinta izlaz)
alg
    oznaka kojom se određuje algoritam rješavanja:
        -'dfs': koristi se funkcija '_dfs_paths'
        -'bfs': koristi se funkcija '_bfs_paths'
        
Returns
-------
put
    lista uređenih parova koji su koordinate traženog puta između 'start' i 'goal'
"""
def get_solution(koordinate, start, goal, alg='dfs'):
    if alg == 'dfs':
        return max(list(_dfs_paths(koordinate, start, goal)), key=len)
    elif alg == 'bfs':
        return max(list(_bfs_paths(koordinate, start, goal)), key=len)

"""
Funkcija koja na temelju liste vrijednosti (svaki je element određen koordinatama na sljedeći način: (x,y) -> x*brojStuapca+y), koja
predstavlja traženi put koji je rješenje algoritma određuje odgovarajuću strukturu podataka, kako bi se labirint mogao riješiti

Tražena struktura je oblika rječnika, koji za ključ ima vrijednost elementa (kako je prethodno opisano), a za vrijednost string duljine
2 slova (npr. 'WE', što znači da trag rješenja [plava linija na slici rješenog labirinta] se u danom elementu kreće od lijeva nadesno)

Parameters
----------
solution_maze1
    lista uređenih parova koji su koordinate traženog puta između ulaza i izlaza labirinta

Returns
-------
orijentacija
    struktura oblika rječnika, koji za ključ ima vrijednost elementa (kako je prethodno opisano), a za vrijednost string duljine
    2 slova (npr. 'WE', što znači da trag rješenja [plava linija na slici rješenog labirinta] se u danom elementu kreće od lijeva nadesno)
"""
def _get_orijent(solution_maze1):
    orijentacija = {}
    beg = ''
    diff = solution_maze1[0] - solution_maze1[1]
    if diff == -1:
        beg = 'W'
        orijentacija[solution_maze1[0]] = 'WE'
    elif diff == 1:
        beg = 'E'
        orijentacija[solution_maze1[0]] = 'EW'
    elif diff > 1:
        beg = 'S'
        orijentacija[solution_maze1[0]] = 'SN'
    else:
        beg = 'N'
        orijentacija[solution_maze1[0]] = 'NS'
    for pos in range(1, len(solution_maze1) - 1):  #barem 2 elementa
        diff = solution_maze1[pos] - solution_maze1[pos + 1]
        if diff > 1:
            orijentacija[solution_maze1[pos]] = beg + 'N'
            beg = 'S'
        elif diff == 1:
            orijentacija[solution_maze1[pos]] = beg + 'W'
            beg = 'E'
        elif diff == -1:
            orijentacija[solution_maze1[pos]] = beg + 'E'
            beg = 'W'
        else:
            orijentacija[solution_maze1[pos]] = beg + 'S'
            beg = 'N'
    if beg == 'S':
        orijentacija[solution_maze1[-1]] = 'SN'
    elif beg == 'N':
        orijentacija[solution_maze1[-1]] = 'NS'
    elif beg == 'E':
        orijentacija[solution_maze1[-1]] = 'EW'
    else:
        orijentacija[solution_maze1[-1]] = 'WE'
    return orijentacija

"""
Funkcija koja na odabarnu sliku elementa labirinta (ovisno o slovu) dodaje trag rješenja [plava linija na slici rješenog labirinta],
ovisno o orijentaciji za dotični element

Parameters
----------
image
    slika koja je objekt klase Image iz PIL-a
orijent
    string duljine 2 znaka, koji predstavlja orijentaciju dotičnog elementa (kako je prethodno opisano)
size
   uređeni par koji predstavlja dimenziju slike image: (width, height)
path:
    uređena trojka objekata klase Image iz PIL-a, koji predatavljaju redom slike:
        -horizontalna plava linija za prikaz rješenja labirinta
        -vertikalna plava linija za prikaz rješenja labirinta
        -plavi kut za prikaz rješenja labirinta
        
Returns
-------
pom_img
    nova slika koja je objekt klase Image iz PIL-a s dodanim tragom rješenja za dotični element labirinta
"""
def _get_image(image, orijent, size, path):
    r_h, r_v, k = path
    pom_img = Image.new("RGB", size)
    pom_img.paste(image, (0, 0))
    if orijent == 'EW' or orijent == 'WE':
        pom_img.paste(r_h, (5, 31))
    elif orijent == 'SN' or orijent == 'NS':
        pom_img.paste(r_v, (31, 5))
    elif orijent == 'SE' or orijent == 'ES':
        pom_img.paste(k.rotate(180), (31, 31))
    elif orijent == 'WS' or orijent == 'SW':
        pom_img.paste(k.rotate(90), (5, 31))
    elif orijent == 'WN' or orijent == 'NW':
        pom_img.paste(k, (5, 5))
    elif orijent == 'NE' or orijent == 'EN':
        pom_img.paste(k.rotate(270), (31, 5))
    return pom_img

"""
Kreiranje slike rješenja labirinta iz 2d polja, čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula
za korištenje) i odgovarajućeg rješenja (lista uređenih parova koji su koordinate traženog puta između ulaza i izlaza labirinta)

Funkcija prikazuje rješenje u obliku plave linije na već postojećoj slici labirinta.
Nakon što završi s kreiranjem slike, pohranjena slika se prikazuje u odgovarajućem programu za pregled.

Parameters
----------
maze
    2d polje čiji je element odgovarajuće slovo (objašnjeno kod funkcije za pripremu modula za korištenje)
row
    broj redaka labirinta
column
    broj stupaca labirinta
maze_name
    ime labirinta koje će se iskoristiti za ime slike labirinta
ends
    uređen par uređenih parova koji predstavljaju koordinate početka i kraja labirinta
open_in
    ukoliko je vrijednost 'browser', slika stabla biti će prikazana u odgovarajućem programu nakon što se završi njeno generiranje
    (kod velikih labirinata to može potrajati do nekoliko minuta)
    
Returns
-------
image
    nova slika koja je objekt klase Image iz PIL-a
"""    
def solve_maze(maze, row, column, solution_maze, maze_name, ends, open_in = 'browser'):
    solution_maze1 = [i*column+j for i,j in solution_maze]
    orijentacija = _get_orijent(solution_maze1)
    open_images = []
    for i in range(1, 7):
        open_images.append(Image.open(f'maze/maze_parts/{i}.png'))
    ravno_hor = Image.open('maze/maze_parts/ravno_hor.png')
    ravno_ver = Image.open('maze/maze_parts/ravno_ver.png')
    krajevi_hor = Image.open('maze/maze_parts/krajevi_hor.png')
    krajevi_ver = Image.open('maze/maze_parts/krajevi_ver.png')
    kut = Image.open('maze/maze_parts/kut.png')
    width, height = open_images[0].size
    blank_image = Image.new("RGB", (width*column, height*row))

    for (i, x) in enumerate(maze):
        h = height * i
        for (j, y) in enumerate(x):
            w = width * j
            if y == 'a':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'b':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'c':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'd':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'e':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'f':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'g':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'h':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'i':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'j':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'k':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'l':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'm':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'n':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'o':
                if i*column+j in orijentacija:
                    new_img = _get_image(_find_image(open_images, y), orijentacija[i*column+j], (width, height), (ravno_hor, ravno_ver, kut))
                    blank_image.paste(new_img, (w,h))
                else:
                    blank_image.paste(_find_image(open_images, y), (w, h))
            elif y == 'p':
                blank_image.paste(_find_image(open_images, y), (w, h))

    beg_image = Image.new('RGB', (width, height))
    beg_image.paste(_find_image(open_images, maze[solution_maze1[0] // column][solution_maze1[0] % column]))
    if orijentacija[solution_maze1[0]] == 'WE':
        beg_image.paste(krajevi_hor.rotate(180), (25, 25))
    elif orijentacija[solution_maze1[0]] == 'EW':
        beg_image.paste(krajevi_hor, (5, 25))
    elif orijentacija[solution_maze1[0]] == 'SN':
        beg_image.paste(krajevi_ver, (25, 5))
    else:
        beg_image.paste(krajevi_ver.rotate(180), (25, 25))
    blank_image.paste(beg_image, (width * (solution_maze1[0] % column), height * (solution_maze1[0] // column)))

    end_image = Image.new('RGB', (width, height))
    end_image.paste(_find_image(open_images, maze[solution_maze1[-1] // column][solution_maze1[-1] % column]))
    if orijentacija[solution_maze1[-1]] == 'WE':
        end_image.paste(krajevi_hor, (5, 25))
    elif orijentacija[solution_maze1[-1]] == 'EW':
        end_image.paste(krajevi_hor.rotate(180), (25, 25))
    elif orijentacija[solution_maze1[-1]] == 'SN':
        end_image.paste(krajevi_ver.rotate(180), (25, 25))
    else:
        end_image.paste(krajevi_ver, (25, 5))
    blank_image.paste(end_image, (width * (solution_maze1[-1] % column), height * (solution_maze1[-1] // column)))

    for i in range(6):
        open_images[i].close()
    ravno_hor.close()
    ravno_ver.close()
    kut.close()
    krajevi_hor.close()
    krajevi_ver.close()
    blank_image = label_ends(ends[0], ends[1], blank_image)
    save_name = f'maze/temp/{time.strftime("%Y%m%d_%H%M%S")}_{maze_name}_solved.jpg'
    blank_image.save(save_name)
    if open_in == 'browser':
        webbrowser.open('file://' + os.getcwd() + '/' + save_name)
    return blank_image

"""
Označavanje početka i kraja na slici labirinta odgovarajućim oznakama

Funkcija na slici labirinta označava ulaz i izlaz iz labirinta sljedećim oznakama:
    -ulaz: žuti kvadratić u sredini odgovarajućeg elementa slike
    -izlaz: zeleni kvadratić u sredini odgovarajućeg elementa slike
    
Nakon što završi s kreiranjem slike, pohranjena slika se prikazuje u odgovarajućem programu za pregled.

Parameters
----------
beg
    uređen par koji je koordinata početka traženja (kod labirinta ulaz)
end
    uređen par koji je koordinata kraja traženja (kod labirinta izlaz)
image
    slika koja je objekt klase Image iz PIL-a
    
Returns
-------
image
    nova slika koja je objekt klase Image iz PIL-a
"""    
def label_ends(beg, end, image):
    image_h = Image.open('maze/maze_parts/1.png')
    width, height = image_h.size
    image_h.close()
    beg_img = Image.open('maze/maze_parts/beg.png')
    end_img = Image.open('maze/maze_parts/end.png')
    image.paste(beg_img, (beg[1]*width+25, beg[0]*height+25))
    image.paste(end_img, (end[1]*width+25, end[0]*height+25))
    beg_img.close()
    end_img.close()
    return image

"""
Kopiranje postojeće slike

Parameters
----------
image
    slika objekta klase Image iz PIL-a za koju želimo kreirati objekt kopiju (deep copy)
    
Returns
-------
image
    nova slika koja je objekt klase Image iz PIL-a
"""    
def copy_image(image):
    return image.copy()

"""
Pohrana postojeće slike

Parameters
----------
image
    slika objekta klase Image iz PIL-a koju želimo pohraniti
name
    naziv slike pod kojim je želimo pohraniti
open_in
    ukoliko je vrijednost 'browser', slika stabla biti će prikazana u odgovarajućem programu nakon što se završi njeno pohranjivanje
    
Returns
-------
image
    ista slika objekta klase Image iz PIL-a koju želimo pohraniti
"""    
def save_image(image, name, open_in=''):
    save_name = f'maze/temp/{time.strftime("%Y%m%d_%H%M%S")}_{name}.jpg'
    image.save(save_name)
    if open_in == 'browser':
        webbrowser.open('file://' + os.getcwd() + '/' + save_name)
    return image

_prepare_module()