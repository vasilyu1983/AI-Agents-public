import math
import unittest
import discrete_information as info


class KnownAnswers(unittest.TestCase):
    def test_entropy_known_answers_and_histogram_bound(self):
        self.assertEqual(info.entropy([1,0]), 0)
        self.assertEqual(info.entropy([.5,.5]), 1)
        self.assertEqual(info.entropy([.25]*4), 2)
        self.assertLessEqual(info.entropy([1/150]*150), math.log2(150)+1e-12)

    def test_joint_dependence(self):
        self.assertEqual(info.mutual_information([[.25,.25],[.25,.25]]), 0)
        self.assertEqual(info.mutual_information([[.5,0],[0,.5]]), 1)

    def test_support_direction_and_js(self):
        self.assertTrue(math.isinf(info.kl([1,0],[0,1])))
        self.assertTrue(math.isinf(info.kl([0,1],[1,0])))
        self.assertEqual(info.js([1,0],[0,1]), 1)
        self.assertEqual(info.kl([.5,.5],[.5,.5]), 0)

    def test_bpb_arithmetic(self):
        self.assertAlmostEqual(info.bpb(2400000*math.log2(12.3),10000000), .8689407385)
        self.assertAlmostEqual(info.bpb(3100000*math.log2(18.7),10000000), 1.3097395732)

    def test_fano_vacuous_and_positive(self):
        self.assertEqual(info.fano_floor(.6,50),0)
        self.assertAlmostEqual(info.fano_floor(2.1,50),1.1/math.log2(50))

    def test_invalid_probability_and_dimensions(self):
        for p in [[], [True,0], [math.nan], [.4,.4], [-1,2]]:
            with self.assertRaises(ValueError): info.entropy(p)
        with self.assertRaises(ValueError): info.kl([1],[.5,.5])
        with self.assertRaises(ValueError): info.mutual_information([[1],[]])
        with self.assertRaises(ValueError): info.fano_floor(2,2)
        with self.assertRaises(ValueError): info.bpb(1,0)


if __name__ == '__main__':
    unittest.main()
