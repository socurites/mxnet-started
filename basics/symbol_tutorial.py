import mxnet as mx

'''
Symobol Composition
'''
# Basic Operators
a = mx.sym.Variable('a')
b = a * 2 + 1
ex = b.bind(ctx=mx.cpu(), args={'a': mx.nd.ones((2, 3))})
ex.forward()
print(ex.outputs)
print(len(ex.outputs))
print(ex.outputs[0].asnumpy())

a = mx.sym.Variable('a')
b = mx.sym.Variable('b')
c = a + b
ex = c.bind(ctx=mx.cpu(), args={'a': mx.nd.ones((2, 3)),
                                'b': mx.nd.full((2, 3), 3)})
ex.forward()
print(ex.outputs)
print(len(ex.outputs))
print(ex.outputs[0].asnumpy())

# Basic Neural Networks
net = mx.sym.Variable('data')
net = mx.sym.FullyConnected(data=net, name='fc1', num_hidden=128)
net = mx.sym.Activation(data=net, name='relu1', act_type="relu")
net = mx.sym.FullyConnected(data=net, name='fc2', num_hidden=10)
net = mx.sym.SoftmaxOutput(data=net, name='out')
vis = mx.viz.plot_network(net, shape={'data': (100, 200)})
vis.render('basic')

# Modulelized Construction for Deep Networks
def ConvFactory(data, num_filter, kernel, stride=(1, 1), pad=(0, 0), name=None, suffix=''):
  conv = mx.symbol.Convolution(data=data, num_filter=num_filter, kernel=kernel, stride=stride, pad=pad,
                               name='conv_%s%s' % (name, suffix))
  bn = mx.symbol.BatchNorm(data=conv, name='bn_%s%s' % (name, suffix))
  act = mx.symbol.Activation(data=bn, act_type='relu', name='relu_%s%s' % (name, suffix))
  return act


prev = mx.symbol.Variable(name="Previos Output")
conv_comp = ConvFactory(data=prev, num_filter=64, kernel=(7, 7), stride=(2, 2))
shape = {"Previos Output": (128, 3, 28, 28)}
vis = mx.viz.plot_network(symbol=conv_comp, shape=shape)
vis.render('conv-factory')


def InceptionFactoryA(data, num_1x1, num_3x3red, num_3x3, num_d3x3red, num_d3x3, pool, proj, name):
  # 1x1
  c1x1 = ConvFactory(data=data, num_filter=num_1x1, kernel=(1, 1), name=('%s_1x1' % name))
  # 3x3 reduce + 3x3
  c3x3r = ConvFactory(data=data, num_filter=num_3x3red, kernel=(1, 1), name=('%s_3x3' % name), suffix='_reduce')
  c3x3 = ConvFactory(data=c3x3r, num_filter=num_3x3, kernel=(3, 3), pad=(1, 1), name=('%s_3x3' % name))
  # double 3x3 reduce + double 3x3
  cd3x3r = ConvFactory(data=data, num_filter=num_d3x3red, kernel=(1, 1), name=('%s_double_3x3' % name),
                       suffix='_reduce')
  cd3x3 = ConvFactory(data=cd3x3r, num_filter=num_d3x3, kernel=(3, 3), pad=(1, 1), name=('%s_double_3x3_0' % name))
  cd3x3 = ConvFactory(data=cd3x3, num_filter=num_d3x3, kernel=(3, 3), pad=(1, 1), name=('%s_double_3x3_1' % name))
  # pool + proj
  pooling = mx.symbol.Pooling(data=data, kernel=(3, 3), stride=(1, 1), pad=(1, 1), pool_type=pool,
                              name=('%s_pool_%s_pool' % (pool, name)))
  cproj = ConvFactory(data=pooling, num_filter=proj, kernel=(1, 1), name=('%s_proj' % name))
  # concat
  concat = mx.symbol.Concat(*[c1x1, c3x3, cd3x3, cproj], name='ch_concat_%s_chconcat' % name)
  return concat


prev = mx.symbol.Variable(name="Previos Output")
in3a = InceptionFactoryA(prev, 64, 64, 64, 64, 96, "avg", 32, name="in3a")
mx.viz.plot_network(symbol=in3a, shape=shape)
vis.render('inception')

# Load and Save
a = mx.sym.Variable('a')
b = a * 2 + 1
ex = b.bind(ctx=mx.cpu(), args={'a': mx.nd.ones((2, 3))})
ex.forward()
print(ex.outputs)
print(len(ex.outputs))
print(ex.outputs[0].asnumpy())
print(b.tojson())

c.save('symbol-b.json')
c2 = mx.symbol.load('symbol-b.json')
print(c.tojson() == c2.tojson())