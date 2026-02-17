frappe.ui.form.on("Makine", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Makine Özeti"), () => {
				show_makine_ozeti(frm);
			});
		}
	},
});

function show_makine_ozeti(frm) {
	frappe.call({
		method: "is_makinesi_erp.api.get_makine_ozeti",
		args: { makine: frm.doc.name },
		callback(r) {
			if (!r.message) return;
			let d = r.message;
			let html = `
				<div class="row">
					<div class="col-sm-6">
						<h6>${__("Puantaj Özeti")}</h6>
						<p>${__("Toplam Çalışma Günü")}: <strong>${d.toplam_gun}</strong></p>
						<p>${__("Toplam Çalışma Saati")}: <strong>${d.toplam_saat}</strong></p>
					</div>
					<div class="col-sm-6">
						<h6>${__("Yakıt Tüketimi")}</h6>
						<p>${__("Toplam Yakıt")}: <strong>${d.toplam_yakit} Lt</strong></p>
						<p>${__("Toplam Yakıt Maliyeti")}: <strong>${format_currency(d.yakit_maliyet)}</strong></p>
					</div>
				</div>
				<div class="row mt-3">
					<div class="col-sm-6">
						<h6>${__("Bakım Maliyeti")}</h6>
						<p>${__("Toplam Bakım Sayısı")}: <strong>${d.bakim_sayisi}</strong></p>
						<p>${__("Toplam Bakım Maliyeti")}: <strong>${format_currency(d.bakim_maliyet)}</strong></p>
					</div>
					<div class="col-sm-6">
						<h6>${__("Toplam Maliyet")}</h6>
						<p><strong>${format_currency(d.toplam_maliyet)}</strong></p>
					</div>
				</div>`;
			frappe.msgprint({ title: __("Makine Özeti: ") + frm.doc.makine_adi, message: html, wide: true });
		},
	});
}
