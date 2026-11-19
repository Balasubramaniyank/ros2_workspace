from setuptools import setup
import os
from glob import glob

package_name = 'ball_follow'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bala',
    maintainer_email='balasubramaniyan.k@zohointern.com',
    description='Tortoisebot with lidar in Python',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
    'console_scripts': [
        
        'follow_ball = ball_follow.followUseNumpy:main',
        'follow=ball_follow.follow:main',
        'mannualcode=ball_follow.ballFollowCodeMannual:main'
    ],
},

)
