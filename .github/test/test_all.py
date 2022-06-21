# -*- coding:utf-8 -*-
import asyncio
import unittest

import yarl

import aiotieba as tb


class ClientTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client: tb.Client = tb.Client('default')
        await self.client.enter()

    async def test_all(self):
        fname = 'starry'
        fid = await self.client.get_fid(fname)
        self.assertGreater(fid, 0)

        user = await self.client.get_self_info()
        user_id = user.user_id
        user = await self.client.get_basic_user_info(user.user_name)
        self.assertEqual(user_id, user.user_id)
        user = await self.client.get_basic_user_info(user.user_id)
        self.assertEqual(user_id, user.user_id)
        user = await self.client.get_user_info(user.user_name)
        self.assertEqual(user_id, user.user_id)
        user = await self.client.get_user_info(user.user_id)
        self.assertEqual(user_id, user.user_id)
        user = (await self.client.get_homepage(user.portrait))[0]
        self.assertEqual(user_id, user.user_id)

        def test_contents(contents: tb.Fragments):
            self.assertIsInstance(contents, tb.Fragments)
            for frag in contents.texts:
                self.assertIsInstance(frag.text, str)
            for frag in contents.emojis:
                self.assertIsInstance(frag.desc, str)
            for frag in contents.imgs:
                self.assertIsInstance(frag.src, str)
                self.assertIsInstance(frag.big_src, str)
                self.assertIsInstance(frag.origin_src, str)
                self.assertIsInstance(frag.hash, str)
                self.assertIsInstance(frag.show_width, int)
                self.assertIsInstance(frag.show_height, int)
            for frag in contents.ats:
                self.assertIsInstance(frag.text, str)
                self.assertIsInstance(frag.user_id, int)
            self.assertIsInstance(contents.voice.voice_md5, str)
            for frag in contents.links:
                self.assertIsInstance(frag.text, str)
                self.assertIsInstance(frag.url, yarl.URL)
                self.assertIsInstance(frag.raw_url, str)
                self.assertIsInstance(frag.is_external, bool)
            for frag in contents.tiebapluses:
                self.assertIsInstance(frag.text, str)
                self.assertIsInstance(frag.url, str)

        def test_comment(comment: tb.Comment):
            self.assertIsInstance(comment.text, str)
            test_contents(comment.contents)

            self.assertEqual(comment.fid, fid)
            self.assertEqual(comment.tid, thread.tid)
            self.assertGreater(comment.pid, 0)
            self.assertNotEqual(comment.author_id, 0)
            self.assertEqual(comment.author_id, comment.user.user_id)
            self.assertIsInstance(comment.agree, int)
            self.assertIsInstance(comment.disagree, int)
            self.assertGreater(comment.create_time, 0)

        threads = await self.client.get_threads(fname)
        self.assertEqual(threads.forum.fid, fid)
        self.assertGreater(len(threads), 0)

        for thread in threads:
            self.assertIsInstance(thread.text, str)
            test_contents(thread.contents)

            self.assertEqual(thread.fid, fid)
            self.assertEqual(thread.fname, fname)
            self.assertGreater(thread.tid, 0)
            self.assertGreater(thread.pid, 0)
            self.assertEqual(thread.author_id, thread.user.user_id)
            self.assertNotEqual(thread.author_id, 0)

            self.assertIsInstance(thread.tab_id, int)
            self.assertIsInstance(thread.is_good, bool)
            self.assertIsInstance(thread.is_top, bool)
            self.assertIsInstance(thread.is_share, bool)
            self.assertIsInstance(thread.is_hide, bool)
            self.assertIsInstance(thread.is_livepost, bool)

            self.assertIsInstance(thread.title, str)
            # test vote
            if thread.tid == 7763555471:
                self.assertIsInstance(thread.vote_info.title, str)
                self.assertIsInstance(thread.vote_info.total_vote, int)
                self.assertIsInstance(thread.vote_info.total_user, int)
                for option in thread.vote_info.options:
                    self.assertIsInstance(option.vote_num, int)
                    self.assertIsInstance(option.text, str)
                    self.assertIsInstance(option.image, str)

            # test share vote
            elif thread.tid == 7870997922:
                self.assertIsInstance(thread.share_origin.text, str)
                test_contents(thread.share_origin.contents)

                self.assertEqual(thread.share_origin.fid, 24677608)
                self.assertEqual(thread.share_origin.fname, 'soulknight')
                self.assertEqual(thread.share_origin.tid, 7870997263)
                self.assertEqual(thread.share_origin.pid, 144377621017)

                self.assertIsInstance(thread.share_origin.title, str)
                self.assertIsInstance(thread.share_origin.vote_info.title, str)
                self.assertIsInstance(thread.share_origin.vote_info.total_vote, int)
                self.assertIsInstance(thread.share_origin.vote_info.total_user, int)
                for option in thread.share_origin.vote_info.options:
                    self.assertIsInstance(option.vote_num, int)
                    self.assertIsInstance(option.text, str)
                    self.assertIsInstance(option.image, str)

            # test posts
            elif thread.tid == 7763274602:
                posts = await self.client.get_posts(thread.tid, with_comments=True)
                self.assertEqual(posts.forum.fid, fid)
                self.assertEqual(posts.thread.tid, thread.tid)
                self.assertGreater(len(posts), 0)

                for post in posts:
                    self.assertIsInstance(post.text, str)
                    test_contents(post.contents)
                    self.assertIsInstance(post.sign, str)
                    for comment in post.comments:
                        test_comment(comment)

                    self.assertEqual(post.fid, fid)
                    self.assertEqual(post.tid, thread.tid)
                    self.assertGreater(post.pid, 0)
                    self.assertNotEqual(post.author_id, 0)
                    self.assertEqual(post.author_id, post.user.user_id)

                    self.assertIsInstance(post.floor, int)
                    self.assertIsInstance(post.reply_num, int)
                    self.assertIsInstance(post.agree, int)
                    self.assertIsInstance(post.disagree, int)
                    self.assertGreater(post.create_time, 0)
                    self.assertEqual(post.is_thread_author, post.author_id == thread.author_id)

                    if post.reply_num > 0:
                        comments = await self.client.get_comments(post.tid, post.pid)
                        self.assertEqual(comments.forum.fid, fid)
                        self.assertEqual(comments.thread.tid, thread.tid)
                        self.assertEqual(comments.post.pid, post.pid)
                        self.assertGreater(len(comments), 0)

                        for comment in comments:
                            test_comment(comment)

            self.assertIsInstance(thread.view_num, int)
            self.assertIsInstance(thread.reply_num, int)
            self.assertIsInstance(thread.share_num, int)
            self.assertIsInstance(thread.agree, int)
            self.assertIsInstance(thread.disagree, int)
            self.assertGreater(thread.create_time, 0)
            self.assertGreater(thread.last_time, 0)

        await self.client.get_recover_list(fname)
        await self.client.get_black_list(fname)
        await self.client.get_recom_list(fname)
        await self.client.get_recom_status(fname)
        await self.client.get_statistics(fname)
        await self.client.get_bawu_dict(fname)
        await self.client.get_tab_map(fname)
        await self.client.get_member_list(fname)
        await self.client.get_forum_detail(fname)

        await self.client.get_self_threads()
        await self.client.get_self_posts()
        await self.client.get_self_forum_list()

        replys = await self.client.get_replys()
        self.assertGreater(len(replys), 0)
        for reply in replys:
            self.assertIsInstance(reply.text, str)
            self.assertIsInstance(reply.fname, str)
            self.assertGreater(reply.tid, 0)
            self.assertGreater(reply.pid, 0)
            self.assertNotEqual(reply.author_id, 0)
            self.assertEqual(reply.author_id, reply.user.user_id)
            self.assertGreater(reply.create_time, 0)
            if reply.is_floor:
                self.assertNotEqual(reply.post_user.user_id, 0)
            self.assertNotEqual(reply.thread_user.user_id, 0)
            self.assertIsInstance(reply.is_floor, bool)
            self.assertGreater(reply.create_time, 0)

        ats = await self.client.get_ats()
        self.assertGreater(len(ats), 0)
        for at in ats:
            self.assertIsInstance(at.text, str)
            self.assertIsInstance(at.fname, str)
            self.assertGreater(at.tid, 0)
            self.assertGreater(at.pid, 0)
            self.assertNotEqual(at.author_id, 0)
            self.assertEqual(at.author_id, at.user.user_id)
            self.assertGreater(at.create_time, 0)
            self.assertIsInstance(at.is_floor, bool)
            self.assertIsInstance(at.is_thread, bool)

    async def asyncTearDown(self):
        await self.client.close()
        await asyncio.sleep(0.25)


class SqlTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client: tb.Reviewer = tb.Reviewer('default', 'asoul')
        await self.client.enter()

    async def test_mysql(self):
        user = await self.client.get_self_info()
        fname = self.client.fname
        fid = await self.client.database.get_fid(fname)
        self.assertEqual(fname, await self.client.database.get_fname(fid))
        await self.client.database.get_basic_user_info(user.user_id)
        await self.client.database.get_basic_user_info(user.user_name)
        await self.client.database.get_basic_user_info(user.portrait)
        await self.client.database.get_tid(fname, 7763274602)
        await self.client.database.get_id(fname, 7763274602)
        await self.client.database.get_user_id_list(fname)
        await self.client.database.get_tid_list(fname, limit=3)

    async def asyncTearDown(self):
        await self.client.close()
        await asyncio.sleep(0.25)


if __name__ == "__main__":
    unittest.main()
