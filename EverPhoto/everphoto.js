const axios = require("axios");

// password 可在网页登录时抓取登录包查看. POST 方法中的 data 内.
phone = "YOUR PHONE NUMBER HERE";
password = "YOUR ENCRYPTED PASSWORD HERE";

function balance() {
	return new Promise(async (resolve) => {
		try {
			let url = "https://web.everphoto.cn/api/auth";
			data = `mobile=%2B86${phone}&password=${password}`;
			let res = await axios.post(url, data);
			token = res.data.data.token;
		} catch (err) {
			console.log("登录失败, " + err.response.data.message);
		}
		resolve();
	});
}

function check() {
	return new Promise(async (resolve) => {
		try {
			let url = "https://api.everphoto.cn/users/self/checkin/v2";
			let res = await axios.post(url, null, {
				headers: { authorization: `Bearer ${token}` },
			});
			let reward_info = res.data.data;
			if (!res.data.code) {
				if (!reward_info.checkin_result) {
					msg = "已签到过...\n";
				} else {
					msg = "签到成功...\n";
				}
				msg += `已连续签到 ${reward_info.continuity} 天, 总共获得 ${
					reward_info.total_reward / 1048576
				}MB, 明日签到可获得 ${
					reward_info.tomorrow_reward / 1048576
				}MB.`;
			} else {
				console.log(`签到失败...\n${res.data}`);
			}
			console.log(msg);
		} catch (err) {
			console.log(err.response.data.message);
		}
		resolve();
	});
}

exports.task = async function (event, context) {
	await balance();
	await check();
};
