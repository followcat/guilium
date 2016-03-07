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
    }
}

def basedesgin_graphviz(config=base_config):
    G = Digraph(name='pet-shop', node_attr={'shape': 'plaintext'})
    G.node('stub', u"""<
    <TABLE>
      <TR>
          <TD PORT="collect" WIDTH="10" COLSPAN="3">%s</TD>
          <TD BGCOLOR="blue" WIDTH="10" COLSPAN="3">%s</TD>
          <TD PORT="collect-out" BGCOLOR="grey" WIDTH="10" COLSPAN="3">%s</TD>
      </TR>
      <TR>
          <TD WIDTH="30" COLSPAN="9" BGCOLOR="chartreuse">stub</TD>
      </TR>
    </TABLE>>""" % (config['stub']['mata'],
                    config['stub']['validator'],
                    config['stub']['collection']),
                    shape='polygon',center='true', sides = '5')
    G.node('SimulatedSUT', shape='box', label="""<
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
    G.node('SUT', shape='box3d', label="""<
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
    G.node('Communication', shape='ellipse')

    G.edge('stub:collect', 'stub:collect-out', color="grey")
    G.edge('stub', 'Communication', label='order', color="grey")
    G.edge('Communication', 'SUT', dir='both', color="red:blue")
    G.edge('stub', 'SimulatedSUT', dir='both', color="red:blue", label='validate')

    return G
