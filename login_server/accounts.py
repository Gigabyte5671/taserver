#!/usr/bin/env python3
#
# Copyright (C) 2018  Maurice van der Pot <griffon26@kfk4ever.com>
#
# This file is part of taserver
# 
# taserver is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# taserver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with taserver.  If not, see <http://www.gnu.org/licenses/>.
#

import base64
import json

from common import utils


class AccountInfo():
    def __init__(self, unique_id, login_name, email_hash, authcode=None, password_hash=None):
        self.unique_id = unique_id
        self.login_name = login_name
        self.email_hash = email_hash
        self.authcode = authcode
        self.password_hash = password_hash

class Accounts():
    def __init__(self, filename):
        self.filename = filename
        self.accounts = {}
        self.load()

    def load(self):
        try:
            with open(self.filename, 'rt') as f:
                data = f.read()
            if data:
                accountlist = json.loads(data)
                for accountentry in accountlist:
                    unique_id = accountentry['unique_id']
                    login_name = accountentry['login_name'].lower()
                    email_hash = accountentry['email_hash']
                    authcode = accountentry['authcode']
                    password_hash = accountentry['password_hash']
                    if password_hash is not None:
                        password_hash = base64.b64decode(password_hash)
                    self.accounts[login_name] = AccountInfo(unique_id,
                                                            login_name,
                                                            email_hash,
                                                            authcode,
                                                            password_hash)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self.filename, 'wt') as f:
            accountlist = []
            for accountinfo in self.accounts.values():
                password_hash = accountinfo.password_hash
                if password_hash is not None:
                    password_hash = base64.b64encode(password_hash).decode('utf-8')
                accountlist.append({
                    'unique_id' : accountinfo.unique_id,
                    'login_name' : accountinfo.login_name.lower(),
                    'email_hash': accountinfo.email_hash,
                    'authcode' : accountinfo.authcode,
                    'password_hash' : password_hash,
                })
            json.dump(accountlist, f, indent = 4)

    def __getitem__(self, key):
        return self.accounts[key.lower()]

    def __contains__(self, key):
        return key.lower() in self.accounts
    
    def update_account(self, login_name, email_hash, authcode):
        login_name = login_name.lower()

        if login_name in self.accounts:
            account = self.accounts[login_name]
            assert account.email_hash == email_hash, "An existing account cannot be updated with a different email hash"
            account.authcode = authcode
        else:
            used_ids = {account.unique_id for account in self.accounts.values()}
            unique_id = utils.first_unused_number_above(used_ids, utils.MIN_VERIFIED_ID, utils.MAX_VERIFIED_ID)
            account = AccountInfo(unique_id, login_name, email_hash, authcode)
            self.accounts[login_name] = account

    def reset_authcode(self, login_name):
        login_name = login_name.lower()
        assert login_name in self.accounts
        if self.accounts[login_name].authcode is not None:
            self.accounts[login_name].authcode = None
            return True
        else:
            return False
