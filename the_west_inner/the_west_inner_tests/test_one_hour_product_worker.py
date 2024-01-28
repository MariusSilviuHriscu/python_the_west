from unittest import mock
import unittest

import sys
#sys.path.insert(0, "the_west_inner")
from crafting import OneHourProductWorker
import unittest
from unittest.mock import Mock
from work import get_closest_workplace_data

class TestOneHourProductWorker(unittest.TestCase):
    def test_must_continue_sleep(self):
        # Test with an empty task queue
        task_queue = Mock()
        task_queue.sleep_task_in_queue.return_value = False
        player_data = Mock()
        player_data.energy = 100
        player_data.energy_max = 100
        worker = OneHourProductWorker(None, task_queue, None, player_data, None)
        self.assertFalse(worker.must_continue_sleep())
        
        # Test with a non-empty task queue
        task_queue = Mock()
        task_queue.sleep_task_in_queue.return_value = True
        player_data = Mock()
        player_data.energy = 100
        player_data.energy_max = 100
        worker = OneHourProductWorker(None, task_queue, None, player_data, None)
        self.assertFalse(worker.must_continue_sleep())
        
        # Test with a non-empty task queue and player energy less than max
        task_queue = Mock()
        task_queue.sleep_task_in_queue.return_value = True
        player_data = Mock()
        player_data.energy = 50
        player_data.energy_max = 100
        worker = OneHourProductWorker(None, task_queue, None, player_data, None)
        self.assertTrue(worker.must_continue_sleep())
        
    def test_get_max_nr_of_tasks(self):
        # Test with premium automation disabled
        task_queue = Mock()
        task_queue.get_tasks_number.return_value = 0
        premium = Mock()
        premium.automation = False
        worker = OneHourProductWorker(None, task_queue, premium, None, None)
        self.assertEqual(worker.get_max_nr_of_tasks(), 4)
        
        # Test with premium automation enabled
        task_queue = Mock()
        task_queue.get_tasks_number.return_value = 0
        premium = Mock()
        premium.automation = True
        worker = OneHourProductWorker(None, task_queue, premium, None, None)
        self.assertEqual(worker.get_max_nr_of_tasks(), 5)
        
        # Test with premium automation enabled and tasks in queue
        task_queue = Mock()
        task_queue.get_tasks_number.return_value = 1
        premium = Mock()
        premium.automation = True
        worker = OneHourProductWorker(None, task_queue, premium, None, None)
        self.assertEqual(worker.get_max_nr_of_tasks(), 4)

    def test_get_coordinates(self):
        # Test with mocked get_closest_workplace_data function
        handler = Mock()
        player_data = Mock()
        work_list = Mock()
        worker = OneHourProductWorker(handler, None, None, player_data, work_list)
        work_list.work_products.return_value = {"product_id": 123}
        get_closest_workplace_data.return_value = (1, 2)
        
        self.assertEqual(worker.get_coordinates(123), (1, 2))
        get_closest_workplace_data.assert_called_with(handler, 123, work_list, player_data)

    def test_work(self):
        # Test with max number of tasks less than number of tasks possible based on energy
        handler = Mock()
        task_queue = Mock()
        task_queue.sleep_task_in_queue.return_value = False
        task_queue.get_tasks_number.return_value = 0
        premium = Mock()
        premium.automation = True
        player_data = Mock()
        player_data.energy = 50
        player_data.energy_max = 100
        work_list = Mock()
        work_list.work_products.return_value = {"product_id": 123}
        coordinates = (1, 2)
        worker = OneHourProductWorker(handler, task_queue, premium, player_data, work_list)
        worker.get_coordinates = Mock(return_value=coordinates)
        
        worker.work()
        self.assertEqual(task_queue.tasks.cancel.call_count, 0)
        self.assertEqual(coordinates.munceste_coord.ore.call_count, 2)
        self.assertEqual(sleep_closest_town.call_count, 1)

        # Test with max number of tasks greater than number of tasks possible based on energy
        handler = Mock()
        task_queue = Mock()
        task_queue.sleep_task_in_queue.return_value = False
        task_queue.get_tasks_number.return_value = 0
        premium = Mock()
        premium.automation = True
        player_data = Mock()
        player_data.energy = 150
        player_data.energy_max = 100
        work_list = Mock()
        work_list.work_products.return_value = {"product_id": 123}
        coordinates = (1,1, 2)
        worker = OneHourProductWorker(handler, task_queue, premium, player_data, work_list)
        worker.get_coordinates = Mock(return_value=coordinates)
        
        worker.work()
        self.assertEqual(task_queue.tasks.cancel.call_count, 0)
        self.assertEqual(coordinates.munceste_coord.ore.call_count, 5)
        self.assertEqual(sleep_closest_town.call_count, 0)
        
        # Test with sleep task in queue
        #handler = Mock()
        #task_queue = Mock()



if __name__ == "__main__":
    unittest.main()
