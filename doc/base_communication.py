from graphviz import Digraph


base_config = {
    'stub': {
        'mata': 'Mata<BR/>validated SUT',
        'validator': 'Validator',
        'collection': 'TestCollection<BR/>origin-outgoing',
    },
    'SimulatedSUT': {
        'material': 'material',
        'engine': 'simulation-engine',
    },
    'SUT': {
        'interface': 'interface',
        'engine': 'engine',
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
    G.node('stub', u"""<
    <TABLE>
      <TR>
          <TD PORT="collect" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="validate" BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="collect-out" BGCOLOR="grey" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="30" COLSPAN="9" BGCOLOR="chartreuse">stub</TD>
      </TR>
    </TABLE>>""" % (config['stub']['mata'],
                    config['stub']['validator'],
                    config['stub']['collection']),
                    shape='diamond',center='true', sides = '5')
    G.node('SimulatedSUT', shape='component', label="""<
    <TABLE>
      <TR>
          <TD BGCOLOR="red" WIDTH="10" COLSPAN="3">%s</TD>
          <TD BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="20" COLSPAN="6" BGCOLOR="chartreuse">SimulatedSUT</TD>
      </TR>
    </TABLE>>""" % (config['SimulatedSUT']['material'],
                    config['SimulatedSUT']['engine']))
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

    G.edge('stub:collect', 'stub:collect-out', color="grey")
    G.edge('stub:collect-out', 'ExCommunication', label='order', color="grey")
    G.edge('ExCommunication', 'SUT', dir='both', color="red:blue")
    G.edge('stub:validate', 'InCommunication', dir='both', color="red:blue", label='validate')
    G.edge('InCommunication', 'SimulatedSUT', dir='both', color="red:blue")

    return G
