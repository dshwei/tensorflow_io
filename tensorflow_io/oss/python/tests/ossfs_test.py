# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for OSS filesystem"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from tensorflow.python.platform import test
from tensorflow.python.platform import gfile
import tensorflow_io.oss.python.ops.ossfs_ops  # pylint: disable=unused-import

if not os.getenv("OSS_CREDENTIALS"):
  sys.exit(
      "OSS_CREDENTIALS env variable not set. Please set it to the "
      "path of your oss credential file."
  )
bucket = os.getenv("OSS_FS_TEST_BUCKET")
if not bucket:
  sys.exit(
      "OSS_FS_TEST_BUCKET env variable not set. Please set it to "
      "your oss bucket"
  )
get_oss_path = lambda p: os.path.join("oss://" + bucket, "oss_fs_test", p)


class OSSFSTest(test.TestCase):
  """OSS Filesystem Tests"""

  @classmethod
  def setUpClass(cls):
    gfile.MkDir(get_oss_path(""))

  @classmethod
  def tearDownClass(cls):
    gfile.DeleteRecursively(get_oss_path(""))

  def test_file_operations(self):
    """ Test file operations"""

    f = get_oss_path("test_file_operations")
    self.assertFalse(gfile.Exists(f))

    fh = gfile.Open(f, mode="w")
    content = "file content"
    fh.write(content)
    fh.close()
    self.assertTrue(gfile.Exists(f))

    fh = gfile.Open(f)
    self.assertEqual(fh.read(), content)

    self.assertEqual(gfile.Stat(f).length, len(content))

    f2 = get_oss_path("test_file_2")
    gfile.Rename(f, f2)
    self.assertFalse(gfile.Exists(f))
    self.assertTrue(gfile.Exists(f2))

  def test_dir_operations(self):
    """ Test directory operations"""

    d = get_oss_path("d1/d2")
    gfile.MakeDirs(d)
    self.assertTrue(gfile.Stat(d).is_directory)

    # Test listing bucket directory with and without trailing '/'
    content = gfile.ListDirectory("oss://" + bucket)
    content_s = gfile.ListDirectory("oss://" + bucket + "/")
    self.assertEqual(content, content_s)
    self.assertIn("oss_fs_test", content)
    self.assertIn("oss_fs_test/d1", content)
    self.assertIn("oss_fs_test/d1/d2", content)

    # Test listing test directory with and without trailing '/'
    content = gfile.ListDirectory("oss://" + bucket + "/oss_fs_test")
    content_s = gfile.ListDirectory("oss://" + bucket + "/oss_fs_test/")
    self.assertEqual(content, content_s)
    self.assertIn("d1", content)
    self.assertIn("d1/d2", content)

    # Test listing sub directories.
    content = gfile.ListDirectory(get_oss_path("d1"))
    content_s = gfile.ListDirectory(get_oss_path("d1/"))
    self.assertEqual(content, content_s)
    self.assertIn("d2", content)

    content = gfile.ListDirectory(get_oss_path("d1/d2"))
    content_s = gfile.ListDirectory(get_oss_path("d1/d2/"))
    self.assertEqual(content, content_s)
    self.assertEqual([], content)


if __name__ == "__main__":
  test.main()
