function getFileInfo(id) {
	return new Promise((resolve, reject) => {
		if (!id) {
			return reject({
				error: true,
				message: "no id was provided..."
			});
		}
		if (id.constructor !== String) {
			return reject({
				error: true,
				message: "id was not of type: String..."
			});
		}

		let input = document.getElementById("testfile");
		if (!input.files[0]) {
			return reject({
				error: true,
				message: "input holds no file..."
			});
		}

		let file = input.files[0];
		return resolve({
			name: file.name.split('.')[0],
			ext: file.name.split('.')[1],
			fullName: file.name,
			size: file.size,
			type: file.type,
			file: file,
			lastModified: file.lastModified,
			lastModifiedDate: file.lastModifiedDate
		});
	});
}

function getFileContents(file) {
	return new Promise((resolve, reject) => {
		if (!file) {
			return reject({
				error: true,
				message: "no file was provided..."
			});
		}
		if (file.constructor !== File) {
			return reject({
				error: true,
				message: "input was not of type: File..."
			});
		}

		var reader = new FileReader();

		reader.addEventListener("load", () => {
			resolve(reader.result);
		}, false);

		if (file) {
			reader.readAsDataURL(file);
		}
	});
}
