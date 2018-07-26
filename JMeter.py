# -*- coding:utf-8 -*- 
# Author: Shiyun Li
# Mail: shiyunl@163.com
# Created Time: Tue Aug 29 14:20:55 2017

import os
import time
from log import logger
import subprocess
import csv
import shutil

from JMeter_Conf import jmeter_conf

class JMeter:
    def __init__(self, c):
        self.jmutils = JMUtils()
        self.__load_properties()

    def __load_properties(self):
        logger.info("Load jmeter properties: ")

        # 加载配置
        self.jmeter_home = jmeter_conf["jmeter_home"]
        self.jmeter_script = jmeter_conf["jmeter_script"]
        self.jmeter_temp_result = jmeter_conf["jmeter_temp_result"]
        self.jmeter_report_types = jmeter_conf["jmeter_report_types"]
        self.jmeter_threads_num = None
        if jmeter_conf.has_key("jmeter_threads_num"):
            self.jmeter_threads_num = jmeter_conf["jmeter_threads_num"]

    def load_dashboard(self, splunk_home, dashboard_path, dashboard_name):
        """
        Splunk Dashboard 测试用例.
        """
        dashboard_file = os.path.join(dashboard_path, dashboard_name)
        target_dir = os.path.join(splunk_home, 'etc', 'apps', 'search', 'local', 'data', 'ui', 'views')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not os.path.exists(os.path.join(target_dir, dashboard_name)):
            shutil.move(dashboard_file, target_dir)

    def run_cmd(self, cmd):
        """
        命令行工具.
        """
        logger.info("Run command: %s", cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ""
        for line in p.stdout.readlines():
            output += line

        return output

    def generate_report(self, jmeter_plugin_cmd, temp_result_folder, temp_result_file, jmeter_report_type):
        """
        Generate jmeter CSV reports such as ResponseTimeOverTime, ResponseCodesPerSecond, AggregateReport.
        """
        logger.info("Generate report: %s", jmeter_report_type)

        temp_file = str(os.path.join(temp_result_folder, str(jmeter_report_type + ".csv")))
        command = "%s --generate-csv %s --input-jtl %s --plugin-type %s" % (
            jmeter_plugin_cmd, temp_file, temp_result_file, jmeter_report_type)

        self.run_cmd(command)

    def parse_file(self, report_file):
        """
        Parse csv file.
        """
        logger.info("Parse file: %s", report_file)

        with open(report_file, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]

        logger.debug("Parse output: %s", rows)
        return rows

    def run_test(self):
        logger.info("Start test: ")

        test_result = {}
        test_result["test_category"] = "JMeter"
        test_result["status"] = "Success"
        test_result["metrics"] = []

        # install dashboard
        self.jmutils.load_dashboard('/opt/splunk', '/opt/testcase/res', 'ui_empty_dashboard.xml')
        self.jmutils.load_dashboard('/opt/splunk', '/opt/testcase/res', 'ui_dashboard.xml')

        # restart splunk
        self.jmutils.restart_splunk('/opt/splunk')

        # jmeter cmd
        jmeter_sh_cmd = str(os.path.join(self.jmeter_home, "bin", "jmeter.sh"))
        jmeter_plugin_cmd = str(os.path.join(self.jmeter_home, "bin", "JMeterPluginsCMD.sh"))

        # run test
        start_time = time.mktime(time.gmtime())
        temp_result_folder = str(os.path.join(self.jmeter_temp_result, "test_" + str(start_time)))
        temp_result_file = str(os.path.join(temp_result_folder, "test_result.jtl"))
        if self.jmeter_threads_num:
            jmeter_command = "%s -JthreadNum=%d -n -t %s -l %s" % (
                jmeter_sh_cmd, self.jmeter_threads_num, self.jmeter_script, temp_result_file)
        else:
            jmeter_command = "%s -n -t %s -l %s" % (jmeter_sh_cmd, self.jmeter_script, temp_result_file)
        end_time = time.mktime(time.gmtime())
        self.jmutils.run_cmd(jmeter_command)

        test_result["start_time"] = start_time
        test_result["end_time"] = end_time
        for jmeter_report_type in self.jmeter_report_types:
            # generate reports
            self.jmutils.generate_report(jmeter_plugin_cmd, temp_result_folder, temp_result_file, jmeter_report_type)
            report_file = str(os.path.join(temp_result_folder, str(jmeter_report_type + ".csv")))
            if not os.path.exists(report_file):
                test_result['status'] = "Fail"

            # upload results
            test_result['metrics'] = self.jmutils.parse_file(report_file)
            logger.info("Upload report: %s", jmeter_report_type)
            self.c.create_result(test_result, jmeter_report_type)

if __name__ == "__main__":
    jm = JMeter()
    jm.run_test()