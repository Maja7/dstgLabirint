import random
import queue
import os
import time
import urllib.request 
from tqdm import tqdm
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import webbrowser

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
            urllib.request.urlretrieve(f'https://github.com/alen-kl/dstgLabirint/blob/master/nikola/maze_parts/{names[i]}?raw=true',
                                       f'maze/maze_parts/{names[i]}')
    print ("Finished downloading images!")

def _createFolder(name):
    path = os.path.join(os.getcwd(), name)
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print ('Error: Creating directory. ' +  name)

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

    graf=[]
    for c in listaCelija1:
        for d in c.children:
            graf.append((c.koordinate,d))



    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments
        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed
        '''

        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                    parent = root)
        return pos

    def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

        '''
        If the graph is a tree this will return the positions to plot this in a 
        hierarchical layout.
        G: the graph (must be a tree)
        root: the root node of current branch 
        - if the tree is directed and this is not given, the root will be found and used
        - if the tree is directed and this is given, then the positions will be just for the descendants of this node.
        - if the tree is undirected and not given, then a random choice will be used.
        width: horizontal space allocated for this branch - avoids overlap with other branches
        vert_gap: gap between levels of hierarchy
        vert_loc: vertical location of root
        xcenter: horizontal location of root
        '''
        if not nx.is_tree(G):
            raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

        if root is None:
            if isinstance(G, nx.DiGraph):
                root = next(iter(nx.topological_sort(G)))
            else:
                root = random.choice(list(G.nodes))

        return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

    G=nx.Graph()

    G.add_edges_from(graf)
    pos=hierarchy_pos(G,korijen)
    nx.draw(G, pos=pos, with_labels=True, node_size=2000)
    save_name = f"maze/temp/{maze_name}.png"
    plt.savefig(save_name)
    if open_in == 'browser':
        webbrowser.open('file://' + os.getcwd() + '/' + save_name)
    maze = _get_letters(koord, brojRedaka, brojStupaca)
    _save_maze(maze, maze_name)
    return koord, maze, (korijen, krajevi.pop(), krajeviNaRubu.pop())

def read_maze(maze_name):
    return [[i for i in line.rstrip('\n')] for line in open(f'maze/mazes_txt/{maze_name}.txt')]
    
def _save_maze(maze, maze_name):
    with open(f'maze/mazes_txt/{maze_name}.txt', 'w') as file:
        for row in maze:
            file.write(''.join(row) + '\n')
            
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

def _dfs_paths(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        for next in [x for x in graph[vertex] if x not in path]:
            if next == goal:
                yield path + [next]
            else:
                stack.append((next, path + [next]))

def _bfs_paths(graph, start, goal):
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in [x for x in graph[vertex] if x not in path]:
            if next == goal:
                yield path + [next]
            else:
                queue.append((next, path + [next]))

def get_solution(koordinate, start, goal, alg='dfs'):
    if alg == 'dfs':
        return max(list(_dfs_paths(koordinate, start, goal)), key=len)
    elif alg == 'bfs':
        return max(list(_bfs_paths(koordinate, start, goal)), key=len)
        
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

def copy_image(image):
    return image.copy()

def save_image(image, name, open_in=''):
    save_name = f'maze/temp/{time.strftime("%Y%m%d_%H%M%S")}_{name}.jpg'
    image.save(save_name)
    if open_in == 'browser':
        webbrowser.open('file://' + os.getcwd() + '/' + save_name)
    return image

_prepare_module()