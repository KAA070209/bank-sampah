-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 26 Feb 2026 pada 15.51
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_bank_sampah`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `detail_setor`
--

CREATE TABLE `detail_setor` (
  `id` int(11) NOT NULL,
  `transaksi_id` int(11) NOT NULL,
  `kategori_id` int(11) NOT NULL,
  `berat` decimal(12,2) NOT NULL,
  `harga` decimal(12,2) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `detail_setor`
--

INSERT INTO `detail_setor` (`id`, `transaksi_id`, `kategori_id`, `berat`, `harga`, `subtotal`) VALUES
(3, 4, 8, 1.00, 8000.00, 8000.00),
(4, 6, 9, 2.00, 45000.00, 90000.00);

-- --------------------------------------------------------

--
-- Struktur dari tabel `kategori_sampah`
--

CREATE TABLE `kategori_sampah` (
  `id` int(11) NOT NULL,
  `nama_kategori` varchar(100) NOT NULL,
  `kelompok` enum('organik','anorganik_low','anorganik_high','b3') NOT NULL,
  `value_level` enum('low','high','-') DEFAULT '-',
  `harga_per_kg` decimal(12,2) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kategori_sampah`
--

INSERT INTO `kategori_sampah` (`id`, `nama_kategori`, `kelompok`, `value_level`, `harga_per_kg`, `deskripsi`, `created_at`, `updated_at`) VALUES
(1, 'Sisa Makanan', 'organik', '-', 500.00, 'Sisa makanan rumah tangga untuk kompos', '2026-02-26 10:25:56', '2026-02-26 10:25:56'),
(2, 'Daun Kering', 'organik', '-', 300.00, 'Daun dan sampah kebun', '2026-02-26 10:25:56', '2026-02-26 10:25:56'),
(3, 'Sayur Busuk', 'organik', '-', 400.00, 'Sayuran tidak layak konsumsi', '2026-02-26 10:25:56', '2026-02-26 10:25:56'),
(4, 'Plastik Kresek', 'anorganik_low', 'low', 1500.00, 'Plastik tipis campuran', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(5, 'Plastik Campur', 'anorganik_low', 'low', 2000.00, 'Plastik berbagai jenis tidak dipilah', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(6, 'Styrofoam', 'anorganik_low', 'low', 1000.00, 'Kemasan styrofoam', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(7, 'Botol PET Bening', 'anorganik_high', 'high', 4500.00, 'Botol plastik bening tanpa label', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(8, 'Kaleng Aluminium', 'anorganik_high', 'high', 8000.00, 'Kaleng minuman aluminium', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(9, 'Tembaga', 'anorganik_high', 'high', 45000.00, 'Logam tembaga kabel', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(10, 'Kardus', 'anorganik_high', 'high', 2500.00, 'Kardus bersih dan kering', '2026-02-26 10:25:56', '2026-02-26 11:05:08'),
(11, 'Aki Bekas', 'b3', '-', 10000.00, 'Aki kendaraan bekas', '2026-02-26 10:25:56', '2026-02-26 10:25:56'),
(12, 'Baterai Bekas', 'b3', '-', 5000.00, 'Baterai rumah tangga', '2026-02-26 10:25:56', '2026-02-26 10:25:56'),
(13, 'Lampu Neon', 'b3', '-', 3000.00, 'Lampu mengandung merkuri', '2026-02-26 10:25:56', '2026-02-26 10:25:56');

-- --------------------------------------------------------

--
-- Struktur dari tabel `log_saldo`
--

CREATE TABLE `log_saldo` (
  `id` int(11) NOT NULL,
  `nasabah_id` int(11) NOT NULL,
  `tipe` enum('setor','penarikan','koreksi') NOT NULL,
  `referensi_id` int(11) NOT NULL,
  `jumlah` decimal(14,2) NOT NULL,
  `saldo_sebelum` decimal(14,2) NOT NULL,
  `saldo_sesudah` decimal(14,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `log_saldo`
--

INSERT INTO `log_saldo` (`id`, `nasabah_id`, `tipe`, `referensi_id`, `jumlah`, `saldo_sebelum`, `saldo_sesudah`, `created_at`) VALUES
(1, 1, 'penarikan', 1, 4500.00, 4500.00, 0.00, '2026-02-26 10:51:53'),
(2, 1, 'penarikan', 3, 8000.00, 8000.00, 0.00, '2026-02-26 10:55:50');

-- --------------------------------------------------------

--
-- Struktur dari tabel `nasabah`
--

CREATE TABLE `nasabah` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `kode_nasabah` varchar(20) NOT NULL,
  `alamat` text DEFAULT NULL,
  `no_hp` varchar(20) DEFAULT NULL,
  `saldo` decimal(14,2) DEFAULT 0.00,
  `total_berat_terkumpul` decimal(14,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `nasabah`
--

INSERT INTO `nasabah` (`id`, `user_id`, `kode_nasabah`, `alamat`, `no_hp`, `saldo`, `total_berat_terkumpul`) VALUES
(1, 2, 'NSB0002', 'Jl.pangauban', '081285554702', 90000.00, 16.00);

-- --------------------------------------------------------

--
-- Struktur dari tabel `notifikasi`
--

CREATE TABLE `notifikasi` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `judul` varchar(200) DEFAULT NULL,
  `pesan` text DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `notifikasi`
--

INSERT INTO `notifikasi` (`id`, `user_id`, `judul`, `pesan`, `is_read`, `created_at`) VALUES
(1, 2, 'Penarikan Disetujui', 'Penarikan Rp 4500.00 telah disetujui admin', 0, '2026-02-26 10:51:53'),
(2, 1, 'Pengajuan Penarikan Baru', 'Muhammad Azka mengajukan penarikan Rp 8000', 0, '2026-02-26 10:55:35'),
(3, 2, 'Penarikan Disetujui', 'Penarikan Rp 8000.00 telah disetujui admin', 0, '2026-02-26 10:55:50');

-- --------------------------------------------------------

--
-- Struktur dari tabel `penarikan`
--

CREATE TABLE `penarikan` (
  `id` int(11) NOT NULL,
  `kode_penarikan` varchar(30) NOT NULL,
  `nasabah_id` int(11) NOT NULL,
  `jumlah` decimal(14,2) NOT NULL,
  `metode` enum('tunai','transfer','ewallet') NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `approved_by` int(11) DEFAULT NULL,
  `tanggal` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `penarikan`
--

INSERT INTO `penarikan` (`id`, `kode_penarikan`, `nasabah_id`, `jumlah`, `metode`, `status`, `approved_by`, `tanggal`) VALUES
(3, 'WD11772103335', 1, 8000.00, 'tunai', 'approved', 1, '2026-02-26 17:55:35');

-- --------------------------------------------------------

--
-- Struktur dari tabel `transaksi_setor`
--

CREATE TABLE `transaksi_setor` (
  `id` int(11) NOT NULL,
  `kode_transaksi` varchar(30) NOT NULL,
  `nasabah_id` int(11) NOT NULL,
  `petugas_id` int(11) DEFAULT NULL,
  `tanggal` datetime DEFAULT current_timestamp(),
  `total_berat` decimal(14,2) NOT NULL,
  `total_harga` decimal(14,2) NOT NULL,
  `status` enum('selesai','dibatalkan') DEFAULT 'selesai'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `transaksi_setor`
--

INSERT INTO `transaksi_setor` (`id`, `kode_transaksi`, `nasabah_id`, `petugas_id`, `tanggal`, `total_berat`, `total_harga`, `status`) VALUES
(4, 'TRX1100', 1, NULL, '2026-02-26 17:53:32', 1.00, 8000.00, 'selesai'),
(6, 'TRX59D0444D59', 1, NULL, '2026-02-26 21:25:44', 2.00, 90000.00, 'selesai');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','petugas','nasabah') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` enum('pending','approved','rejected') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `nama`, `username`, `email`, `password`, `role`, `is_active`, `last_login`, `created_at`, `updated_at`, `status`) VALUES
(1, 'admin', 'admin', 'admin@gmail.com', 'scrypt:32768:8:1$r1Nnjco832lyV8uH$902daa2c9a00e5951f1711a3af74bd48ea2af3cf3c77d3748d8dc4b6925ce08642ece078d4bf6306311decb150cef9ab25ed672fba03046b10efa300ae4e1c96', 'admin', 1, NULL, '2026-02-26 09:29:52', '2026-02-26 09:29:52', 'approved'),
(2, 'Muhammad Azka', 'azka', NULL, 'scrypt:32768:8:1$ILVDnwekkAUPiYdz$493e476f7d1599d8bc8bdc8c3a5fa6dfbbc6a9f7fdce94b2bd4d42823a1b77f0a6212046cbed983fd76b4986c234535f33bc9241960df0106a30b253125b3e85', 'nasabah', 1, NULL, '2026-02-26 09:32:30', '2026-02-26 09:39:48', 'approved');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `detail_setor`
--
ALTER TABLE `detail_setor`
  ADD PRIMARY KEY (`id`),
  ADD KEY `transaksi_id` (`transaksi_id`),
  ADD KEY `kategori_id` (`kategori_id`);

--
-- Indeks untuk tabel `kategori_sampah`
--
ALTER TABLE `kategori_sampah`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `log_saldo`
--
ALTER TABLE `log_saldo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `nasabah_id` (`nasabah_id`);

--
-- Indeks untuk tabel `nasabah`
--
ALTER TABLE `nasabah`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kode_nasabah` (`kode_nasabah`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `penarikan`
--
ALTER TABLE `penarikan`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kode_penarikan` (`kode_penarikan`),
  ADD KEY `nasabah_id` (`nasabah_id`),
  ADD KEY `approved_by` (`approved_by`);

--
-- Indeks untuk tabel `transaksi_setor`
--
ALTER TABLE `transaksi_setor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kode_transaksi` (`kode_transaksi`),
  ADD KEY `nasabah_id` (`nasabah_id`),
  ADD KEY `petugas_id` (`petugas_id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `detail_setor`
--
ALTER TABLE `detail_setor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `kategori_sampah`
--
ALTER TABLE `kategori_sampah`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT untuk tabel `log_saldo`
--
ALTER TABLE `log_saldo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `nasabah`
--
ALTER TABLE `nasabah`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `penarikan`
--
ALTER TABLE `penarikan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `transaksi_setor`
--
ALTER TABLE `transaksi_setor`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `detail_setor`
--
ALTER TABLE `detail_setor`
  ADD CONSTRAINT `detail_setor_ibfk_1` FOREIGN KEY (`transaksi_id`) REFERENCES `transaksi_setor` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detail_setor_ibfk_2` FOREIGN KEY (`kategori_id`) REFERENCES `kategori_sampah` (`id`);

--
-- Ketidakleluasaan untuk tabel `log_saldo`
--
ALTER TABLE `log_saldo`
  ADD CONSTRAINT `log_saldo_ibfk_1` FOREIGN KEY (`nasabah_id`) REFERENCES `nasabah` (`id`);

--
-- Ketidakleluasaan untuk tabel `nasabah`
--
ALTER TABLE `nasabah`
  ADD CONSTRAINT `nasabah_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  ADD CONSTRAINT `notifikasi_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Ketidakleluasaan untuk tabel `penarikan`
--
ALTER TABLE `penarikan`
  ADD CONSTRAINT `penarikan_ibfk_1` FOREIGN KEY (`nasabah_id`) REFERENCES `nasabah` (`id`),
  ADD CONSTRAINT `penarikan_ibfk_2` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`);

--
-- Ketidakleluasaan untuk tabel `transaksi_setor`
--
ALTER TABLE `transaksi_setor`
  ADD CONSTRAINT `transaksi_setor_ibfk_1` FOREIGN KEY (`nasabah_id`) REFERENCES `nasabah` (`id`),
  ADD CONSTRAINT `transaksi_setor_ibfk_2` FOREIGN KEY (`petugas_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
