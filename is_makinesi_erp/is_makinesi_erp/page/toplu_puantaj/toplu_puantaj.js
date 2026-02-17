frappe.pages["toplu-puantaj"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Toplu Puantaj Girişi",
		single_column: true,
	});

	new TopluPuantaj(page);
};

class TopluPuantaj {
	constructor(page) {
		this.page = page;
		this.rows = [];
		this.make_filters();
		this.make_body();
		this.make_buttons();
	}

	make_filters() {
		this.puantaj_tipi = this.page.add_field({
			fieldname: "puantaj_tipi",
			label: __("Puantaj Tipi"),
			fieldtype: "Select",
			options: "Makine Puantaj\nPersonel Puantaj",
			default: "Makine Puantaj",
			change: () => this.refresh_table(),
		});

		this.tarih = this.page.add_field({
			fieldname: "tarih",
			label: __("Tarih"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		});

		this.proje = this.page.add_field({
			fieldname: "proje",
			label: __("Proje"),
			fieldtype: "Link",
			options: "Project",
			reqd: 1,
		});
	}

	make_body() {
		this.body = $('<div class="toplu-puantaj-body"></div>').appendTo(
			this.page.body
		);
		this.table_area = $(
			'<div class="toplu-puantaj-table mt-4"></div>'
		).appendTo(this.body);
		this.refresh_table();
	}

	make_buttons() {
		this.page.set_primary_action(__("Satır Ekle"), () => this.add_row());
		this.page.set_secondary_action(__("Kaydet"), () => this.save_all());
	}

	refresh_table() {
		this.rows = [];
		this.table_area.empty();

		let is_makine = this.puantaj_tipi.get_value() === "Makine Puantaj";
		let resource_label = is_makine ? __("Makine") : __("Personel");
		let extra_cols = is_makine
			? `<th>${__("Operatör")}</th><th>${__("Yakıt (Lt)")}</th>`
			: `<th>${__("Mesai Saati")}</th>`;

		this.table_area.html(`
			<table class="table table-bordered table-sm">
				<thead>
					<tr>
						<th style="width:30px">#</th>
						<th>${resource_label}</th>
						<th>${__("Çalışma Saati")}</th>
						${extra_cols}
						<th>${__("Açıklama")}</th>
						<th style="width:40px"></th>
					</tr>
				</thead>
				<tbody class="puantaj-rows"></tbody>
			</table>
		`);

		this.add_row();
	}

	add_row() {
		let idx = this.rows.length + 1;
		let is_makine = this.puantaj_tipi.get_value() === "Makine Puantaj";
		let row = { idx, controls: {} };

		let $tr = $("<tr></tr>");
		$tr.append(`<td>${idx}</td>`);

		// Resource link
		let $resource_td = $("<td></td>").appendTo($tr);
		row.controls.resource = frappe.ui.form.make_control({
			df: {
				fieldtype: "Link",
				options: is_makine ? "Makine" : "Employee",
				fieldname: "resource_" + idx,
				placeholder: is_makine ? __("Makine seçin") : __("Personel seçin"),
			},
			parent: $resource_td,
			render_input: true,
		});

		// Çalışma saati
		let $saat_td = $("<td></td>").appendTo($tr);
		row.controls.calisma_saati = frappe.ui.form.make_control({
			df: {
				fieldtype: "Float",
				fieldname: "calisma_saati_" + idx,
				placeholder: "8",
				default: 8,
			},
			parent: $saat_td,
			render_input: true,
		});
		row.controls.calisma_saati.set_value(8);

		if (is_makine) {
			// Operatör
			let $op_td = $("<td></td>").appendTo($tr);
			row.controls.operator = frappe.ui.form.make_control({
				df: {
					fieldtype: "Link",
					options: "Employee",
					fieldname: "operator_" + idx,
					placeholder: __("Operatör"),
				},
				parent: $op_td,
				render_input: true,
			});

			// Yakıt
			let $yakit_td = $("<td></td>").appendTo($tr);
			row.controls.yakit = frappe.ui.form.make_control({
				df: {
					fieldtype: "Float",
					fieldname: "yakit_" + idx,
					placeholder: "0",
				},
				parent: $yakit_td,
				render_input: true,
			});
		} else {
			// Mesai saati
			let $mesai_td = $("<td></td>").appendTo($tr);
			row.controls.mesai_saati = frappe.ui.form.make_control({
				df: {
					fieldtype: "Float",
					fieldname: "mesai_saati_" + idx,
					placeholder: "0",
					default: 0,
				},
				parent: $mesai_td,
				render_input: true,
			});
			row.controls.mesai_saati.set_value(0);
		}

		// Açıklama
		let $aciklama_td = $("<td></td>").appendTo($tr);
		row.controls.aciklama = frappe.ui.form.make_control({
			df: {
				fieldtype: "Data",
				fieldname: "aciklama_" + idx,
				placeholder: __("Açıklama"),
			},
			parent: $aciklama_td,
			render_input: true,
		});

		// Sil butonu
		let $del_td = $("<td></td>").appendTo($tr);
		$(`<button class="btn btn-xs btn-danger">
			<i class="fa fa-trash"></i>
		</button>`)
			.appendTo($del_td)
			.on("click", () => {
				$tr.remove();
				this.rows = this.rows.filter((r) => r !== row);
			});

		this.table_area.find(".puantaj-rows").append($tr);
		this.rows.push(row);
	}

	collect_data() {
		let tarih = this.tarih.get_value();
		let proje = this.proje.get_value();
		let puantaj_tipi = this.puantaj_tipi.get_value();

		if (!tarih || !proje) {
			frappe.throw(__("Tarih ve Proje alanları zorunludur"));
		}

		let entries = [];
		for (let row of this.rows) {
			let resource = row.controls.resource.get_value();
			let calisma_saati = row.controls.calisma_saati.get_value();

			if (!resource) continue;

			let entry = { resource, calisma_saati };

			if (puantaj_tipi === "Makine Puantaj") {
				entry.operator = row.controls.operator
					? row.controls.operator.get_value()
					: null;
				entry.yakit_tuketimi = row.controls.yakit
					? row.controls.yakit.get_value() || 0
					: 0;
			} else {
				entry.mesai_saati = row.controls.mesai_saati
					? row.controls.mesai_saati.get_value() || 0
					: 0;
			}

			entry.aciklama = row.controls.aciklama
				? row.controls.aciklama.get_value()
				: "";

			entries.push(entry);
		}

		if (!entries.length) {
			frappe.throw(__("En az bir kayıt girmelisiniz"));
		}

		return { tarih, proje, puantaj_tipi, entries };
	}

	save_all() {
		let data;
		try {
			data = this.collect_data();
		} catch (e) {
			return;
		}

		frappe.call({
			method: "is_makinesi_erp.api.toplu_puantaj_kaydet",
			args: { data: JSON.stringify(data) },
			freeze: true,
			freeze_message: __("Puantaj kayıtları oluşturuluyor..."),
			callback: (r) => {
				if (r.message) {
					let result = r.message;
					if (result.errors && result.errors.length) {
						let msg = result.errors
							.map((e) => `<li>${e}</li>`)
							.join("");
						frappe.msgprint({
							title: __("Bazı kayıtlar oluşturulamadı"),
							indicator: "orange",
							message: `<ul>${msg}</ul>`,
						});
					}
					if (result.created > 0) {
						frappe.show_alert(
							{
								message: __(
									"{0} puantaj kaydı başarıyla oluşturuldu",
									[result.created]
								),
								indicator: "green",
							},
							5
						);
						this.refresh_table();
					}
				}
			},
		});
	}
}
