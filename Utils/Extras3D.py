import matplotlib as mpl
from PyQt5.QtGui import QVector3D, QQuaternion, QMatrix4x4
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from math import pi

DPC = 100000
RAD2DEG = 180 / pi


def rotate(vector, axis, angle):
    """Rotate Q3DVector vector along the given Q3DVector axis on the given float angle using QMatrix4x4.
    :param vector: Q3DVector -- vector to rotate
    :param axis: Q3DVector -- vector of axis direction (normalized)
    :param angle: float -- angle of rotation
    :return: Q3DVector -- rotated vector
    """
    if angle == 0:
        return vector

    m = QMatrix4x4()
    m.rotate(angle * RAD2DEG, axis)
    result = m * vector
    result.normalize()

    # result = QQuaternion.fromAxisAndAngle(axis, angle).rotatedVector(vector)

    return result


def get_circle_segment_3d(
        begin_point,  # радиус-вектор начала сегмента
        moving_direction,  # тангенциаль начала сегмента (нормированый 3d вектор)
        center_direction,  # нормаль начала сегмента (нормированый 3d вектор)
        length,  # длина сегмента
        radius):  # радиус изгиба сегмента
    """ Get points of circle segment of given length, radius, begin_point, center_direction and moving_direction.
    :param begin_point: Q3DVector -- radius-vector of starting point of circle segment
    :param moving_direction: Q3DVector -- tangential vector for the segment in begin_point
    :param center_direction: Q3DVector -- normal vector to the center of the segment in begin_point
    :param length: float -- length of the segment
    :param radius: float -- radius of the circle
    :return: list of points present the segment, moving_direction in the last point, center_direction in the last point
    """
    # dpcs = int(DPC / (2 * pi * radius) * length)
    # delta_alpha = 2 * pi / DPC

    dpcs = DPC * length
    delta_alpha = 1 / (radius * DPC)

    center = begin_point + center_direction * radius
    axis = QVector3D.crossProduct(moving_direction, center_direction)

    points = []
    for i in range(int(dpcs)):
        direction = rotate(vector=center_direction, axis=axis, angle=i * delta_alpha)
        point = center - direction * radius
        points.append(point)

    center_direction_next = rotate(vector=center_direction, axis=axis, angle=(dpcs-1) * delta_alpha)
    moving_direction_next = QVector3D.crossProduct(center_direction_next, axis)
    return points, moving_direction_next, center_direction_next


if __name__ == "__main__":
    test = "main"
    if test == "main":
        mpl.rcParams['legend.fontsize'] = 10

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plt.gca().set_aspect('equal', adjustable='box')

        points = []
        bp = QVector3D(0.0, 0.0, 0.0)
        md = QVector3D(0.0, -1.0, 0.0)
        cd = QVector3D(0.0, 0.0, 1.0)
        l = 0.25
        r = 0.40

        _points, _moving_direction, _center_direction = get_circle_segment_3d(
            bp,
            md,
            cd,
            l,
            r)
        points += _points

        cd = rotate(_center_direction, _moving_direction, pi / 2)
        _points, _moving_direction, _center_direction = get_circle_segment_3d(
            _points[-1],
            _moving_direction,
            cd,
            l,
            r)
        points += _points

        x = [point.x() for point in points]
        y = [point.y() for point in points]
        z = [point.z() for point in points]

        ax.plot(x, y, z, label='parametric curve')
        ax.legend()
        ax.set_xlim([-20, 20])
        ax.set_ylim([-20, 20])
        ax.set_zlim([-20, 20])

        plt.show()
    elif test == "rotate":
        x = QVector3D(1.0, 0.0, 0.0)
        y = QVector3D(0.0, 1.0, 0.0)
        z = QVector3D(0.0, 0.0, 1.0)
        a = pi / 4

        r = rotate(x, y, a)

        print(r)
