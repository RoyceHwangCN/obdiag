#!/usr/bin/env python
# -*- coding: UTF-8 -*
# Copyright (c) 2022 OceanBase
# OceanBase Diagnostic Tool is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

"""
@time: 2023/9/26
@file: verify.py
@desc:
"""
import decimal
import re
import subprocess32 as subprocess
from common.logger import logger
from handler.checker.check_exception import VerifyFalseException, VerifyFailException
from handler.meta.check_meta import GlobalCheckMeta
from utils.utils import parse_range_string


class VerifyResult(object):
    # There are three types of validation results: pass; VerifyFailException (if an exception occurs during the
    # validation process, handle it as fail); VerifyException (verification failed, report needs to be combined with
    # report_type)
    def __init__(self, expr, env_dict, now_step_set_value_name, verify_type="base"):
        self.expr = expr
        self.env_dict = env_dict
        self.verify_type = verify_type
        self.now_step_set_value_name = now_step_set_value_name

    def execute(self):
        logger.debug("verify_result execute")
        logger.info("verify_type input is {0}".format(self.verify_type))
        if self.verify_type is None or self.verify_type == "":
            self.verify_type = "base"
            logger.info("verify_type input is {0}, to set base".format(self.verify_type))
        if self.verify_type == "base":
            return self._verify_base()
        elif self.verify_type == "between":
            return self._verify_between()
        elif self.verify_type == "max":
            return self._verify_max()
        elif self.verify_type == "min":
            return self._verify_min()
        elif self.verify_type == "equal":
            return self._verify_equal()
        else:
            return self._verify_base()

    def _verify_between(self):
        try:
            result = parse_range_string(self.expr, self.env_dict[self.now_step_set_value_name])
        except Exception as e:
            logger.error("parse_range_string error: " + self.expr + "->" + e.__str__())
            raise VerifyFailException(e)
        return result

    def _verify_base(self):
        check_verify_shell = GlobalCheckMeta().get_value(key="check_verify_shell")
        try:
            logger.debug("the result verify is {0}".format(self.expr))
            real_shell = re.sub(r'\$\{([^}]+)\}', self.expr, check_verify_shell)
            for env in self.env_dict:
                logger.debug("add env: {0} ,the value:{1} , the type:{2}".format(env, self.env_dict[env],
                                                                                 type(self.env_dict[env])))
                if isinstance(self.env_dict[env], int):
                    real_shell = env + '=' + str(self.env_dict[env]) + '\n' + real_shell
                else:
                    real_shell = env + '="' + str(self.env_dict[env]) + '"\n' + real_shell
            logger.debug("real_shell: {0}".format(real_shell))
            process = subprocess.Popen(real_shell, shell=True, stdout=subprocess.PIPE)
            out, err = process.communicate()
            process.stdout.close()
            result = out[:-1].decode('utf-8')
            logger.info("_verify_base result: {0}".format(result))
            return result == "true"
        except Exception as e:
            logger.error("_verify_base error: {0} -> {1}".format(str(self.expr) , e))
            raise VerifyFailException("_verify_base error: " + self.expr + "->" + e.__str__())

    def _verify_max(self):
        try:
            if isinstance(self.env_dict[self.now_step_set_value_name],decimal.Decimal):
                self.env_dict[self.now_step_set_value_name]=int(self.env_dict[self.now_step_set_value_name])
            if not isinstance(self.env_dict[self.now_step_set_value_name],int):
                raise Exception("{0} is {1} and the type is {2}, not int or decimal !".format(self.now_step_set_value_name, self.env_dict[self.now_step_set_value_name],type(self.env_dict[self.now_step_set_value_name])))
            range_str = self.expr
            result = int(self.env_dict[self.now_step_set_value_name]) < int(range_str)
            return result
        except Exception as e:
            logger.error("_verify_max error: {0} -> {1}".format(str(self.expr) , e))
            raise VerifyFalseException(e)

    def _verify_min(self):
        try:
            if isinstance(self.env_dict[self.now_step_set_value_name],decimal.Decimal):
                self.env_dict[self.now_step_set_value_name]=int(self.env_dict[self.now_step_set_value_name])
            if not isinstance(self.env_dict[self.now_step_set_value_name],int):
                raise Exception("{0} is {1} and the type is {2}, not int or decimal !".format(self.now_step_set_value_name, self.env_dict[self.now_step_set_value_name],type(self.env_dict[self.now_step_set_value_name])))
            range_str = self.expr
            result=int(self.env_dict[self.now_step_set_value_name]) > int(range_str)
            return result
        except Exception as e:
            logger.error("_verify_min error: {0} -> {1}".format(str(self.expr),e))
            raise VerifyFalseException(e)

    def _verify_equal(self):
        try:
            if isinstance(self.env_dict[self.now_step_set_value_name],decimal.Decimal):
                self.env_dict[self.now_step_set_value_name]=int(self.env_dict[self.now_step_set_value_name])
            if not isinstance(self.env_dict[self.now_step_set_value_name],int):
                raise Exception("{0} is {1} and the type is {2}, not int or decimal !".format(self.now_step_set_value_name, self.env_dict[self.now_step_set_value_name],type(self.env_dict[self.now_step_set_value_name])))
            result = False
            range_str = self.expr
            if int(self.env_dict[self.now_step_set_value_name]) == int(range_str):
                result = True
        except Exception as e:
            logger.error("_verify_equal error: {0} -> {1}".format(str(self.expr),e))
            raise VerifyFailException(e)
        return result


