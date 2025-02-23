from minipypy.objects import module

class Module(module.Module):

    interpleveldefs = {
        'range'         : 'functional.range_int'
    }
