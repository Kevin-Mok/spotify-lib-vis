from django.test import TestCase
from .views import update_std_dev
import math
# Create your tests here.

class UpdateStdDevTest(TestCase):

    def test_two_data_points(self):
        """
        tests if update_std_dev behaves correctly for two data points
        """
        cur_mean = 5
        cur_std_dev = 0

        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, 10, 2)

        self.assertTrue(math.isclose(new_mean, 7.5, rel_tol=0.01))
        self.assertTrue(math.isclose(new_std_dev, 3.5355, rel_tol=0.01))


    def test_three_data_points(self):
        """
        tests if update_std_dev behaves correctly for three data points
        """
        cur_mean = 7.5
        cur_std_dev = 3.5355

        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, 15, 3)

        self.assertTrue(math.isclose(new_mean, 10, rel_tol=0.01))
        self.assertTrue(math.isclose(new_std_dev, 5, rel_tol=0.01))


    def test_four_data_points(self):
        """
        tests if update_std_dev behaves correctly for four data points
        """
        cur_mean = 10 
        cur_std_dev = 5 

        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, 20, 4) 
        self.assertTrue(math.isclose(new_mean, 12.5, rel_tol=0.01))
        self.assertTrue(math.isclose(new_std_dev, 6.455, rel_tol=0.01))


    def test_five_data_points(self):
        """
        tests if update_std_dev behaves correctly for five data points
        """
        cur_mean = 12.5
        cur_std_dev = 6.455 

        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, 63, 5) 
        self.assertTrue(math.isclose(new_mean, 22.6, rel_tol=0.01)) 
        self.assertTrue(math.isclose(new_std_dev, 23.2658, rel_tol=0.01))

    
    def test_sixteen_data_points(self):
        """
        tests if update_std_dev behaves correctly for sixteen data points
        """
        cur_mean = 0.4441 
        cur_std_dev = 0.2855 

        new_mean, new_std_dev = update_std_dev(cur_mean, cur_std_dev, 0.7361, 16) 
        self.assertTrue(math.isclose(new_mean, 0.4624, rel_tol=0.01)) 
        self.assertTrue(math.isclose(new_std_dev, 0.2853, rel_tol=0.01))