# coding=utf-8
import xlrd
from igraph import *
import datetime


color_dict = {0: "pink", 1: "green",2:"purple",3:"orange",4:"blue",5:"yellow",6:"red",7:"#8B2500",8:"#87CEEB",9:"#707070",
              10:"#FFF68F",11:"#FFEFD5",12:"#FFE4E1",13:"#FFDEAD",14:"#FFC1C1",15:"#FFB90F",16:"#FFA54F",17:"#FF8C00",
              18:"black",19:"#FF6EB4",20:"#FF4500",21:"#FF3030",22:"#F5DEB3",23:"#F0FFFF",24:"#F08080",25:"#EED2EE",26:"#EECFA1",
              27:"#EECBAD",28:"#EEC900",29:"#DDA0DD",30:"#E3E3E3",31:"#DB7093",32:"#D8BFD8",33:"#D2B48C",34:"#CDCDB4",
              35:"#CDAD00",36:"#CD853F",37:"#CD5555",38:"#CAE1FF",39:"#BCEE68",40:"#A0522D",41:"#AEEEEE",42:"#9AFF9A",
43:"#B03060",44:"#8B6508",45:"#8B475D",46:"#8B1A1A",47:"#836FFF",48:"#7A378B",49:"#76EEC6",50:"#698B69"}


class NetworkAnalysis:

    def __init__(self, matrix_file, label_file=None, algorithm="BGLL"):
        self.matrix_file = matrix_file
        self.label_file = label_file
        self.algorithm = algorithm
        self.graph, self.weights, self.label, self.matrix = self.createGraph()
        self.result, self.listresult, self.Q = self.community_detect()
        self.drawGraph()

    def read_data(self):

        # 读取矩阵文件
        data = xlrd.open_workbook(self.matrix_file)
        table = data.sheets()[0]
        nrows = table.nrows
        max_node = 0 # 最大的点数
        tuple = [] # 记录点边集合
        for i in xrange(0,nrows):
            rowValues = table.row_values(i)
            node_i, node_j, value = int(rowValues[0]), int(rowValues[1]), float(rowValues[2])
            tuple.append(rowValues)
            if max_node < node_i:
                max_node = node_i
            if max_node < node_j:
                max_node = node_j

        matrix = [[0 for i in range(max_node+1)] for j in range(max_node+1)]
        for t in tuple:
            node_i, node_j, value = int(t[0]), int(t[1]), float(t[2])
            matrix[node_i][node_j] = value

        # 读取标签文件
        if self.label_file is None:
            label_list = [i for i in range(max_node+1)]
        else:
            data = xlrd.open_workbook(self.label_file)
            table = data.sheets()[0]
            nrows = table.nrows
            label_list = ["" for j in range(max_node+1)]
            for i in xrange(0, nrows):
                rowValues = table.row_values(i)
                node, label = int(rowValues[0]), rowValues[1]
                label_list[node] = label
                print rowValues

        return matrix, label_list

    def createGraph(self):
        matrix, labels = self.read_data()
        nodes = matrix.__len__()
        g = Graph(nodes)
        g.vs["name"] = labels
        g.vs["label"] = labels
        edges = []
        weights = []
        for i in range(0, nodes, 1):
            for j in range(0, nodes, 1):
                if matrix[i][j] > 0:
                    edges += [(i,j)]
                    weights.append(matrix[i][j])
        g.add_edges(edges)
        return g, weights, labels, matrix


    def community_detect(self):

        starttime = datetime.datetime.now()
        if self.algorithm == "BGLL":
            result = self.graph.community_multilevel(self.weights)
            Q = self.graph.modularity(result, self.weights)
        elif self.algorithm == "walktrap":
            se = self.graph.community_walktrap(self.weights, steps=5)
            ss = se.as_clustering()
            result = [[] for i in range(ss.__len__())]
            for i in range(0,ss.__len__(), 1):
                result[i] = (ss.__getitem__(i))
            Q = self.graph.modularity(ss, self.weights)
        elif self.algorithm == 'fastgreedy':
            se = self.graph.community_fastgreedy(self.weights)
            ss = se.as_clustering()
            result = [[] for i in range(ss.__len__())]
            for i in range(0, ss.__len__(), 1):
                result[i] = (ss.__getitem__(i))
            Q = ss.recalculate_modularity()
        elif self.algorithm == 'LPA':
            print "y"
            se = self.graph.community_label_propagation(weights=self.weights)
            result = [[] for i in range(se.__len__())]
            for i in range(0, se.__len__(), 1):
                result[i] = (se.__getitem__(i))
            Q = se.recalculate_modularity()
        else:
            result = None
            Q = None
        listresult = [0 for i in range(self.graph.vcount())]
        for i in range(0, result.__len__(), 1):
            for j in range(0, result[i].__len__(), 1):
                listresult[result[i][j]] = i
        endtime = datetime.datetime.now()
        print (endtime - starttime)
        print "模块度", Q
        return result, listresult, Q

    def drawGraph(self):
        self.graph = self.graph.simplify(self.graph)
        layout = self.graph.layout_graphopt()
        # layout = self.graph.layout("fr")
        v_size = [10 for i in range(self.matrix.__len__(),1)]
        plot(self.graph,edge_width=0.5,vertex_color=[color_dict[i % 50] for i in self.listresult])
        # p = Plot()
        # p.background = "#ffffff"  # 将背景改为白色，默认是灰色网格
        # p.add(self.graph,
        #       bbox=(50, 50, 550, 550),  # 设置图占窗体的大小，默认是(0,0,600,600)
        #       layout=layout,  # 图的布局
        #       vertex_size=v_size,  # 点的尺寸
        #       edge_width=0.5, edge_color="grey",  # 边的宽度和颜色，建议灰色，比较好看
        #       vertex_label_size=10,  # 点标签的大小
        #       vertex_color=[color_dict[i % 50] for i in self.listresult])  # 为每个点着色
        # p.show()
        # p.save("SNA.png")  # 将图保存到特定路径，igraph只支持png和pdf
        # p.remove(self.graph)

# matrix_file = "data/空手道俱乐部/kkk2.xls"
# matrix_file = "data/足球数据集/football_data.xls"
matrix_file = "data/悲惨世界人物关系77节点/l_data.xls"
label_file=None
algorithm = "LPA"
NetworkAnalysis(matrix_file, label_file, algorithm)

# g = Graph.Famous("petersen")
# plot(g)