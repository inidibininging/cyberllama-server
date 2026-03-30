import sqlite3
import random
import logging
import os

COL_ID=0
COL_CHARACTER=1
COL_LINE=2
COL_PARENT=3
COL_LOCATION=4
COL_FACTION=5
COL_MOOD=6

COL_SPEAKER_ID=0
COL_TAGS=1

class Sqlite3CacheService:
    def __init__(self, config):
        self.config = config

    def cache_db_init(self):
        # if self.config.db.initialized == False:
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS cached_dialogue (id TEXT, character TEXT, line TEXT, parent TEXT, location TEXT, faction TEXT, mood TEXT)")
        conn.close()
                
    def cache_db_init_world_data(self):
        # if self.config.db.initialized == False:
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS world_data (id TEXT, session TEXT, time TEXT,health DOUBLE, max_health DOUBLE, armor DOUBLE, gender TEXT, location_name TEXT, quest_name TEXT, quest_objective TEXT, lifepath TEXT, district TEXT, sub_district TEXT, food DOUBLE, hydration DOUBLE, fun DOUBLE, relationship DOUBLE, combat_state TEXT, combat_time TEXT, combat_last_combat TEXT, combat_duration TEXT, npc_id_hash TEXT, npc_record_id_hash TEXT, npc_class_name TEXT, npc_display_name TEXT, npc_tweaks_name TEXT, npc_appearance TEXT, npc_gender TEXT, npc_voice TEXT, npc_voice_arg TEXT, npc_voice_pitch TEXT, is_main_npc TEXT, npc_backstory TEXT, npc_moods TEXT, last_action TEXT)")
        conn.close()

    def cache_db_init_npc_cache(self):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        # id, character, line, npc_id_hash, record_id_hash, created_at
        cur.execute("CREATE TABLE IF NOT EXISTS npc_cache_line (id TEXT, character TEXT, line TEXT, id_hash TEXT, record_id_hash TEXT, created_at DATETIME)")
        conn.close()

    def cache_db_init_npc_mood(self):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        # id, character, mood, value, id_hash, record_id_hash, created_at
        cur.execute("CREATE TABLE IF NOT EXISTS npc_mood (id TEXT, character TEXT, mood TEXT, value TEXT, id_hash TEXT, record_id_hash TEXT, created_at DATETIME)")
        conn.close()

    def cache_db_init_location_description(self):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        # id, district, sub_district, x, y, z, description, created_at
        cur.execute("CREATE TABLE IF NOT EXISTS location_description (id TEXT, district TEXT, sub_district, x REAL, y REAL, z REAL, description TEXT, created_at DATETIME)")
        conn.close()
    
    #  Retrieves the line of a character by its line content '''
    def cache_db_get_dialog_line_by_line(self, character='', line='', limit=None, offset=None):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        sql = "SELECT * FROM cached_dialogue WHERE character = ? and trim(replace(lower(line),' ','')) = ?"
        params = [character, line.strip()]
        if(limit):
            sql = sql + " LIMIT ?"
            params.append(limit)            
            if(offset):
                sql = sql + " OFFSET ?"
                params.append(offset)
        sql = sql + ";"
        rc = cur.execute(sql, params)
        res = rc.fetchall()
        conn.close()
        return res

    def cache_db_get_lines_by_parent(self, id, limit=None, offset=None):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        sql = "SELECT * FROM cached_dialogue WHERE parent = ?"
        params = [id]
        if(limit):
            sql = sql + " LIMIT ?"
            params.append(limit)            
            if(offset):
                sql = sql + " OFFSET ?"
                params.append(offset)
        sql = sql + ";"
        rc = cur.execute(sql, params)
        res = rc.fetchall()
        conn.close()
        return res

    def cache_db_get_random_lines_by_parent(self, parent_db_line, character='',count=1):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()

        params = [parent_db_line[COL_ID]]
        sqlc = "select count(*) from cached_dialogue where parent = ?;"
        rcc = cur.execute(sqlc, params)
        rcc = rcc.fetchall()
        if(len(rcc) == 0):
            return []
        if(int(rcc[0][0]) == 0):
            return []
        rcc = str(rcc[0][0])
        sql = "select id, character, line, parent, location, faction, mood from cached_dialogue where parent = " + "'" + parent_db_line[COL_ID] + "' and character = " + "'" + character + "'" + " limit " + str(count) + " offset (select abs(random()) % (" +  rcc + " - 1) + 1);"
        rc = cur.execute(sql)
        res = rc.fetchall()
        return res

    def update_entity(self, entity, table_name, fields, whereSqlCondition):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()                
        cur.execute(
            "UPDATE " +
            table_name +
            " SET " +
            ",".join(
                list(
                    map(
                        lambda f: f + " = ?",
                        fields
                    )
                )
            ) +
            " WHERE " +
            where,
            tuple(
                list(
                    map(
                        lambda f: getattr(entity, f),
                        fields
                    )
                )
            )
        )
        conn.commit()
        conn.close()

    def insert_entity(self, entity, table_name, fields):
        conn = sqlite3.connect(self.config.db.path)        
        cur = conn.cursor()
        columns = list(
                    map(
                        lambda f: "?", 
                        fields
                    )
                )

        # index = 0
        tbescaped = []

        def _conv(f):
            val = getattr(entity, f)
            if type(val) == int or type(val) == float:
                return "\'" + str(float(val)) + "\'"
            elif type(val) is dict:
                tbescaped.append(val)
                if table_name == 'world_data':
                    return "\'" + str(val['td']).rjust(2, '0') + \
                    'd' + " " + \
                    str(val['th']).rjust(2, '0') + ":" + \
                    str(val['tm']).rjust(2, '0') + ":" + \
                    str(val['ts']).rjust(2, '0') + "\'"
                return ''
            elif type(val) is list:
                return "\'" + "[" + ",".join(list(map(lambda x: str(x).replace("'", "\'"), val))) + "]" + "\'"# for now. later on => use conv with an additional muted arg
            elif val == None:
                return 'NULL'
            else:
                return "\'" + val.replace("'", "") + "\'"    

        values_unsafe =  ",".join(list(
                            map(
                                _conv,
                                fields
                            )
                        ))

        sql = "INSERT INTO " + table_name + " (" + \
                ",".join(fields)  + \
                ") VALUES (" +  \
                values_unsafe + \
                ")"
        cur.execute(
            sql,
            # values
        )
        conn.commit()
        conn.close()

    def save_world_data(self, world_data):      
        fields = [
                "id",
                "session",
                "time",
                "health",
                "max_health",
                "armor",
                "gender",
                "location_name",
                "quest_name",
                "quest_objective",
                "lifepath",
                "district",
                "sub_district",
                "food",
                "hydration",
                "fun",
                "relationship",
                "combat_state",
                "combat_time",
                "combat_last_combat",
                "combat_duration",
                "npc_id_hash",
                "npc_record_id_hash",
                "npc_class_name",
                "npc_display_name",
                "npc_tweaks_name",
                "npc_appearance",
                "npc_gender",
                "npc_voice",
                "npc_voice_engine",
                "npc_voice_arg",
                "npc_speaker_id",
                "npc_voice_pitch",
                "is_main_npc",
                "npc_backstory",
        ]
        self.insert_entity(
            world_data,
            'world_data',
            fields
        )

    def cache_db_add_line(self, id, character, line, parent, location='', faction='', mood=''):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        if not mood or mood == '':
            mood = self.get_mood_of_prompt(line)
        cur.execute( \
            "INSERT INTO cached_dialogue (id, character, line, parent, location, faction, mood) VALUES (?, ?, ?, ?, ?, ?, ?);",\
                (id, character, self.clean_text(line), parent, location, faction, mood))
        conn.commit()
        conn.close()

    # adds npc and v lines to cache
    # later on, fetching just a little piece of cache via limit can be useful
    def cache_db_add_npc_line(self, id, character, line, id_hash, record_id_hash):
        created_at = str(datetime.datetime.now())
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute( \
            "INSERT INTO npc_cache_line (id, character, line, id_hash, record_id_hash, created_at) VALUES (?, ?, ?, ?, ?, ?);",\
                (str(id), character, self.clean_text(line), id_hash, record_id_hash, created_at))
        conn.commit()
        conn.close()

    def cache_db_add_location_description(self, id, district, sub_district, x, y, z, description):
        # id, district, sub_district, x, y, z, description, created_at
        created_at = str(datetime.datetime.now())
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute( \
            "INSERT INTO location_description (id, district, sub_district, x, y, z, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",\
                (str(id), district, sub_district, x, y, z, description, created_at))
        conn.commit()
        conn.close()

    def cache_db_add_npc_mood(self, id, character, mood, value, id_hash, record_id_hash):
        created_at = str(datetime.datetime.now())
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute( \
            "INSERT INTO npc_mood (id, character, mood, value, id_hash, record_id_hash, created_at) VALUES (?, ?, ?, ?, ?, ?);",\
                (str(id), character, mood, value, npc_id_hash, record_id_hash, created_at))
        conn.commit()
        conn.close()
    
    def cache_db_update_npc_mood_by_id(self, id, character, mood, value, id_hash, record_id_hash):
        now = datetime.datetime.now()
        created_at = str(datetime.datetime.now())
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute( \
            """
            UPDATE npc_mood 
            SET mood = ?,
            SET value = ?
            WHERE id = ?;
            """,\
            (mood, value, str(id)))
        conn.commit()
        conn.close()
    
    def cache_db_update_npc_mood_by_game_ids(self, id, character, mood, value, id_hash, record_id_hash):
        now = datetime.datetime.now()
        created_at = str(datetime.datetime.now())
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        cur.execute( \
            """
            UPDATE npc_mood 
            SET mood = ?,
            SET value = ?            
            WHERE 
            character = ? AND
            id_hash = ? AND
            record_id_hash = ?;
            """,\
            (mood, value, character, id_hash, record_id_hash))
        conn.commit()
        conn.close()

    def cache_db_add_vlines(self, dialogue_entries):
        conn = sqlite3.connect(self.config.db.path)
        cur = conn.cursor()
        
        for dialog_line in dialogue_entries:
            cur.execute( \
                "INSERT INTO cached_dialogue (id, character, line, parent, location) VALUES (?, ?, ?, ?, ?);",\
                    (dialog_line[0], dialog_line[1], dialog_line[2], dialog_line[3], ''))
            conn.commit()                    
                    # (uuid.uuid4(), character, dialog_line, parent))
        conn.close()