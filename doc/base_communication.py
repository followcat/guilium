from graphviz import Digraph


base_config = {
    'app': {
        'mata': 'Mata<BR/>validated SUT',
        'validator': 'Validator',
        'collection': 'TestCollection<BR/>origin-outgoing',
    },
    'stub': {
        'material': 'material',
        'engine': 'simulation-engine',
    },
    'SUT': {
        'interface': 'interface',
        'engine': 'engine',
    },
    'SimulatedSUT': {
        'material': 'material',
        'engine': 'simulation-engine',
    },
    'InValidator': {
        'validate': 'Validator',
    },
    'INCOM': {
        'comm': 'Internal<BR/>Communication',
    },
    'EXCOM': {
        'comm': 'External<BR/>Communication',
    },
}

def basedesgin_graphviz(config=base_config):
    G = Digraph(name='pet-shop', node_attr={'shape': 'plaintext'})
    G.node('app', u"""<
    <TABLE>
      <TR>
          <TD PORT="validate" BGCOLOR="yellow" WIDTH="30" COLSPAN="9">%s</TD>
      </TR>
      <TR>
          <TD PORT="collect" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="collect-out" BGCOLOR="grey" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="30" COLSPAN="9" BGCOLOR="chartreuse">application</TD>
      </TR>
    </TABLE>>""" % (config['app']['validator'],
                    config['app']['mata'],
                    config['app']['collection']),
                    shape='egg',center='true')
    G.node('stub', shape='component', label="""<
    <TABLE>
      <TR>
          <TD BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="engine" BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">stub</TD>
      </TR>
    </TABLE>>""" % (config['stub']['material'],
                    config['stub']['engine']))
    G.node('SUT', shape='component', label="""<
    <TABLE>
      <TR>
          <TD BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">SUT</TD>
      </TR>
    </TABLE>>""" % (config['SUT']['interface'],
                    config['SUT']['engine']))
    G.node('SimulatedSUT', shape='component', label="""<
    <TABLE>
      <TR>
          <TD BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="engine" BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">SimulatedSUT</TD>
      </TR>
    </TABLE>>""" % (config['SimulatedSUT']['material'],
                    config['SimulatedSUT']['engine']))
    G.node('InValidator', label="""<
    <TABLE>
      <TR>
          <TD>%s</TD>
      </TR>
      <TR><TD>Internal<BR/>Validator</TD></TR>
    </TABLE>>""" % (config['InValidator']['validate']), color='yellow', shape='doublecircle')
    G.node('ExCommunication', label="""<
    <TABLE>
        <TR>
            <TD>%s</TD>
        </TR>
    </TABLE>>""" % (config['EXCOM']['comm']), shape='box3d')
    G.node('InCommunication', label="""<
    <TABLE>
        <TR>
            <TD>%s</TD>
        </TR>
    </TABLE>>""" % (config['INCOM']['comm']), shape='box')

    G.edge("app:collect", "app:collect-out", color="grey")
    G.edge("ExCommunication", 'SUT', dir="both", color="red:blue")
    G.edge("stub", "app:validate", color="blue", label="storage")
    G.edge("stub:engine", "InCommunication", label="order", color="grey")
    G.edge("stub:engine", "ExCommunication", dir="both", label="order", color="grey:blue")
    G.edge("InCommunication", "SimulatedSUT", label="order", color="grey")
    G.edge("SimulatedSUT:engine", "InValidator", label="storage", color="blue")

    return G

basedesgin_graphviz()
