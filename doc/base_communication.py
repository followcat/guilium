from graphviz import Digraph


base_config = {
    'app': {
        'mata': 'Mata<BR/>validated SUT',
        'collection': 'TestCollection<BR/>origin-outgoing',
    },
    'stub': {
        'material': 'Material',
        'validator': 'Validator',
    },
    'ValidatedSUT': {
        'interface': 'Interface',
        'engine': 'Engine',
    },
    'SUT': {
        'interface': 'Interface',
        'engine': 'Engine',
    },
    'SimulatedSUT': {
        'material': 'Material',
        'engine': 'Simulation-Engine',
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
    G.node('app', shape='egg', center='true', label="""<
    <TABLE>
      <TR>
          <TD PORT="collect" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="collect-out" BGCOLOR="grey" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="30" COLSPAN="9" BGCOLOR="chartreuse">application</TD>
      </TR>
    </TABLE>>""" % (config['app']['mata'],
                    config['app']['collection']))
    G.node('stub', shape='component', label="""<
    <TABLE>
      <TR>
          <TD PORT="material" BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="validator" BGCOLOR="yellow" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">stub</TD>
      </TR>
    </TABLE>>""" % (config['stub']['material'],
                    config['stub']['validator']))
    G.node('ValidatedSUT', shape='component', label="""<
    <TABLE>
      <TR>
          <TD BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">ValidatedSUT</TD>
      </TR>
    </TABLE>>""" % (config['ValidatedSUT']['interface'],
                    config['ValidatedSUT']['engine']))
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
    G.edge("app:collect-out", "stub:material", color="grey", label="order")
    G.edge("stub", "InCommunication", label="order", color="grey")
    G.edge("stub", "ExCommunication", label="order", color="grey")
    G.edge("ExCommunication", 'ValidatedSUT', dir="both", color="red:blue")
    G.edge("ExCommunication", "stub:validator", label="storage", color="blue")
    G.edge("ExCommunication", 'SUT', dir="both", color="red:blue")
    G.edge("InCommunication", "SimulatedSUT", label="order", color="grey")
    G.edge("SimulatedSUT:engine", "InValidator", label="storage", color="blue")

    return G

basedesgin_graphviz()
