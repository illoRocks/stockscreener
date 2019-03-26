from stockscreener.cli import main
from datetime import datetime
import time
import re

if __name__ == "__main__":
    main()

    # t1 = time.time()

    # l = """
    # hallo
    # test\n
    # 123
    # """
    # i = 0
    # while i < 1000:
    #     i += 1
    #     x = l.replace('\n', '')

    # t2 = time.time()
    
    # i = 0
    # while i < 1000:
    #     i += 1
    #     x = re.sub('\n', '', l)

    # t3 = time.time()

    # print(t2-t1)
    # print(t3-t2)

    # import cProfile

    # profile_file = 'logs/main_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.profile'

    # profile = cProfile.Profile()
    # profile.run('main()')
    # profile.dump_stats(profile_file) 
    # profile.print_stats()



# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

# graphviz = GraphvizOutput()
# graphviz.output_file = 'basic.png'

# with PyCallGraph(output=graphviz):
#     main()

# import profile

