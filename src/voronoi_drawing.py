from base_drawing import BaseDrawing


class VoronoiDrawing(BaseDrawing):

    def get_command_line_args(self):
        parser.add_argument("filename", type=str)
        parser.add_argument("vertices", type=int)
        parser.add_argument("--power", type=float, default=1.0)
        parser.add_argument("--floor", type=float, default=0)
        parser.add_argument("--ceil", type=float, default=255)
        parser.add_argument('--rotate', dest='rotate', action='store_true')
        parser.set_defaults(rotate=False)
        return args
