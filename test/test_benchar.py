import unittest
import os

from exact_string_matching import forward
from lib.benchar import benchar

if os.environ.get('CBENCHAR') is not None:
  from lib.benchar.build import cbenchar

class TestBenchar(unittest.TestCase):
  run_cbenchar = unittest.skipUnless(
    os.environ.get('CBENCHAR', False),
    'Skip test unless CBENCHAR variable specified')

  def test_same_benchar(self):
    test_benchar = benchar.Benchar()
    list(forward.brute_force(
      test_benchar('#abrakababra'), test_benchar('#brak'), 11, 4))
    self.assertEqual(test_benchar.cmp_count, 12)

  def test_different_benchars(self):
    test_benchar_t, test_benchar_w = benchar.Benchar(), benchar.Benchar()
    list(forward.brute_force(
      test_benchar_t('#abrakrdabra'), test_benchar_w('#ra'), 11, 2))
    self.assertEqual(test_benchar_t.cmp_count + test_benchar_w.cmp_count, 13)

  def test_benchar_str(self):
    test_benchar = benchar.Benchar()
    list(forward.brute_force(test_benchar('#abrbkababra'), '#br', 11, 2))
    self.assertEqual(test_benchar.cmp_count, 14)

  def test_str_benchar(self):
    test_benchar = benchar.Benchar()
    list(forward.brute_force('#bbrakababra', test_benchar('#brak'), 11, 4))
    self.assertEqual(test_benchar.cmp_count, 13)

  @run_cbenchar
  def test_same_cbenchar(self):
    test_benchar = cbenchar.Benchar()
    list(forward.brute_force(
      test_benchar('#abrakababra'), test_benchar('#brak'), 11, 4))
    self.assertEqual(test_benchar.cmp_count, 12)

  @run_cbenchar
  def test_different_cbenchars(self):
    test_benchar_t = cbenchar.Benchar()
    test_benchar_w = cbenchar.Benchar()
    list(forward.brute_force(
      test_benchar_t('#abrakrdabra'), test_benchar_w('#ra'), 11, 2))
    self.assertEqual(test_benchar_t.cmp_count + test_benchar_w.cmp_count, 13)

  @run_cbenchar
  def test_cbenchar_str(self):
    test_benchar = cbenchar.Benchar()
    list(forward.brute_force(test_benchar('#abrbkababra'), '#br', 11, 2))
    self.assertEqual(test_benchar.cmp_count, 14)

  @run_cbenchar
  def test_str_cbenchar(self):
    test_benchar = cbenchar.Benchar()
    list(forward.brute_force('#bbrakababra', test_benchar('#brak'), 11, 4))
    self.assertEqual(test_benchar.cmp_count, 13)
