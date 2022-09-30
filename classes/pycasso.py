import json
from sect.triangulation import Triangulation
from ground.base import get_context
import matplotlib.pyplot as plt


class Pycasso:
    def __init__(self, plt, logger):
        self.plt = plt
        self.pause_time = 0
        self.logger = logger

    def handle_polygon(self, main_polygon, max_vertexes, desc_title, map_file, data_file):
        result = {
                    'main_polygon_coords': main_polygon,
                    'convexity': self.is_convex(main_polygon),
                    'splitting_strategy': 'None',
                    'polygons_coords': None,
                 }

        self.logger.info('Num. vertexes: %i' % len(main_polygon))
        self.logger.info('Maximum number of vertexes per polygon: %i' % max_vertexes)
        self.logger.info('Convexity: %s' % result['convexity'])

        if self.plt is not None:
            xpoly, ypoly = zip(*main_polygon)
            self.plt.figure()
            # self.plt.plot(xpoly, ypoly, marker=".", markersize=10)
            self.plt.plot(xpoly, ypoly, linewidth=3)
            self.plt.grid()
            self.plt.xlabel('X')
            self.plt.ylabel('Y')
            self.plt.pause(1)

        # Check the number of the vertexes
        if len(main_polygon) > max_vertexes:

            # If the polygon is not convex
            if result['convexity'] is False:
                result['polygons_coords'] = self.do_triangles(main_polygon)
                result['splitting_strategy'] = 'Delaunay triangulation'

                self.logger.info('Found %i triangles' % len(result['polygons_coords']))

                if self.plt is not None:

                    str_title = '%s\n[Vertexes: %i (max %i); Convexity: %s; Found polygons: %i]' % (desc_title,
                                                                                                    len(main_polygon),
                                                                                                    max_vertexes,
                                                                                                    result['convexity'],
                                                                                                    len(result['polygons_coords']))
                    self.plt.title(str_title)

                    self.plot_polygons(result['polygons_coords'])
            else:
                result['polygons_coords'] = self.split_convex_polygon(main_polygon, max_vertexes)
                result['splitting_strategy'] = 'Coverage via polygons'

                self.logger.info('Found %i polygons' % len(result['polygons_coords']))

                if self.plt is not None:

                    str_title = '%s\n[Vertexes: %i (max %i); Convexity: %s; Found polygons: %i]' % (desc_title,
                                                                                                    len(main_polygon),
                                                                                                    max_vertexes,
                                                                                                    result['convexity'],
                                                                                                    len(result['polygons_coords']))
                    self.plt.title(str_title)
                    self.plot_polygons(result['polygons_coords'])

        else:
            if self.plt is not None:
                str_title = '%s\n[Vertexes: %i (max %i)]' % (desc_title, len(main_polygon), max_vertexes)
                self.plt.title(str_title)

        # Save results
        if data_file is not None:
            with open(data_file, 'w') as fp:
                json.dump(result, fp, indent=4)

        if self.plt is not None:
            if map_file is not None:
                self.plt.savefig(map_file)

            else:
                self.plt.show()
            self.plt.close()

            # Plot the empty polygon
            str_title = '%s' % desc_title
            self.plt.figure()
            self.plt.plot(xpoly, ypoly, linewidth=3)
            self.plt.grid()
            self.plt.xlabel('X')
            self.plt.ylabel('Y')
            self.plt.title(str_title)
            self.plt.savefig(map_file.replace('.png', '_empty.png'))
            self.plt.close()

        return result

    @staticmethod
    def split_convex_polygon(coords, size_polygons):
        num_polygons = int(len(coords) / size_polygons)
        size_last_polygon = 0
        if len(coords) % size_polygons > 0:
            num_polygons += 1
            size_last_polygon = len(coords) - (size_polygons * (num_polygons-1))

        polygons = dict()

        for i in range(0, num_polygons):
            offset = i * size_polygons

            if (i < num_polygons - 1) or (i == num_polygons - 1 and (size_last_polygon == 0 or size_last_polygon >= 3)):
                polygons[i] = []

                if i == num_polygons-1 and size_last_polygon > 0:
                    num_points = size_last_polygon

                # Check if the last dataset is not enough for a polygons
                elif i == num_polygons - 2 and 0 < size_last_polygon < 3:
                    num_points = size_polygons + size_last_polygon - 1

                else:
                    num_points = size_polygons

                if i > 0:
                    polygons[i].append([coords[0][0], coords[0][1]])
                    polygons[i].append([coords[offset - 1][0], coords[offset - 1][1]])
                for j in range(0, num_points):
                    polygons[i].append([coords[j+offset][0], coords[j+offset][1]])
                polygons[i].append([coords[0][0], coords[0][1]])

        return polygons

    def plot_polygons(self, polygons_dict):
        for polygon_key in polygons_dict.keys():
            self.logger.info('Polygon: %05i/%05i' % (polygon_key, len(polygons_dict)))
            xpl, ypl = zip(*polygons_dict[polygon_key])
            self.plt.plot(xpl, ypl, linestyle='dashed')
            if self.pause_time > 0:
                self.plt.pause(self.pause_time)

    @staticmethod
    def is_convex(coords):
        first_value = 0
        for k in range(0, len(coords)-2):
            # Go one point ahead
            dx1 = coords[k + 1][0] - coords[k][0]
            dy1 = coords[k + 1][1] - coords[k][1]

            # Go two points ahead
            dx2 = coords[k + 2][0] - coords[k + 1][0]
            dy2 = coords[k + 2][1] - coords[k + 1][1]

            zcrossproduct = dx1 * dy2 - dy1 * dx2

            if first_value == 0:
                first_value = zcrossproduct
            else:
                if first_value * zcrossproduct < 0:
                    # The polygon is not convex
                    return False
        # The polygon is convex
        return True

    @staticmethod
    def do_triangles(coords):
        context = get_context()
        contour, point = context.contour_cls, context.point_cls

        points = []
        for coord in coords:
            points.append(point(coord[0], coord[1]))
        contour = contour(points)
        polygon_instance = context.polygon_cls
        polygon = polygon_instance(contour, [])
        triangles_raw = Triangulation.constrained_delaunay(polygon, context=context).triangles()

        triangles = {}
        for i in range(0, len(triangles_raw)):
            triangles[i] = []
            for v in triangles_raw[i].vertices:
                triangles[i].append([v.x, v.y])
            triangles[i].append([triangles_raw[i].vertices[0].x, triangles_raw[i].vertices[0].y])
        return triangles


# Main
if __name__ == "__main__":

    max_vertexes_number = 4

    main_polygon = [[1, 1], [2, 1], [2, 2], [1, 2], [0.5, 1.5]]
    # main_polygon = [[1, 1], [2, 1], [2, 2], [1, 2], [1.5, 1.5]]
    main_polygon = [[1, 1], [2, 1], [2, 2], [2, 2.5], [1.8, 1.6], [1.2, 2.4], [1.5, 1.5]]
    # main_polygon = [[1, 1], [1.6, 1.1], [1.8, 1.5], [2, 2], [2, 2.5], [1.8, 3.6], [1.7, 3.7], [1.6, 3.8], [1.4, 3.65], [1.2, 3.5], [0.8, 3.1], [0.6, 2.8], [0.5, 2.5], [0.5, 1.85], [0.65, 1.3]]
    main_polygon.append(main_polygon[0])

    pycasso = Pycasso(plt=plt)

    res = pycasso.handle_polygon(main_polygon=main_polygon, max_vertexes=max_vertexes_number, pause_time=0.5,
                                 desc_title='test', map_file='test.png', data_file='data.json')
                                 # desc_title='test', output_file=None)

    # print('res')
    # print(res)

