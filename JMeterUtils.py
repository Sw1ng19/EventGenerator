# -*- coding:utf-8 -*- 
# Author: Shiyun Li
# Mail: shiyunl@163.com
# Created Time: Tue Aug 29 14:20:55 2017

from log import logger
import subprocess
import csv
import os
import shutil

class JMUtils:
    def copy_dashboard(self, splunk_home, dashboard_path, dashboard_name):
        """
        Test case, copy some dashboards to target Splunk.
        pay attention about the os.path and shutil packages usage.
        """
        dashboard_file = os.path.join(dashboard_path, dashboard_name)
        target_dir = os.path.join(splunk_home, 'etc', 'apps', 'search', 'local', 'data', 'ui', 'views')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not os.path.exists(os.path.join(target_dir, dashboard_name)):
            shutil.move(dashboard_file, target_dir)

    def run_cli_command(self, cmd):
        """
        Run command line and fetch results.
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

        self.run_cli_command(command)

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