import React from "react";
import { TextField, Button } from "@mui/material";

const ContactForm = () => (
  <section id="contact" className="py-20 bg-gray-900 text-white">
    <div className="container mx-auto text-center px-6">
      <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
        Contact Us
      </h2>
      <form className="mt-10 max-w-md mx-auto space-y-6">
        <TextField
          fullWidth
          label="Your Name"
          variant="outlined"
          InputLabelProps={{ style: { color: "rgba(255, 255, 255, 0.7)" } }}
          InputProps={{
            style: { color: "white", borderColor: "rgba(255, 255, 255, 0.5)" },
          }}
          sx={{
            "& .MuiOutlinedInput-root": {
              "& fieldset": {
                borderColor: "rgba(255, 255, 255, 0.5)",
              },
              "&:hover fieldset": {
                borderColor: "#7f5af0",
              },
              "&.Mui-focused fieldset": {
                borderColor: "#7f5af0",
              },
            },
          }}
        />
        <TextField
          fullWidth
          label="Your Email"
          variant="outlined"
          InputLabelProps={{ style: { color: "rgba(255, 255, 255, 0.7)" } }}
          InputProps={{
            style: { color: "white", borderColor: "rgba(255, 255, 255, 0.5)" },
          }}
          sx={{
            "& .MuiOutlinedInput-root": {
              "& fieldset": {
                borderColor: "rgba(255, 255, 255, 0.5)",
              },
              "&:hover fieldset": {
                borderColor: "#7f5af0",
              },
              "&.Mui-focused fieldset": {
                borderColor: "#7f5af0",
              },
            },
          }}
        />
        <TextField
          fullWidth
          label="Your Message"
          variant="outlined"
          multiline
          rows={4}
          InputLabelProps={{ style: { color: "rgba(255, 255, 255, 0.7)" } }}
          InputProps={{
            style: { color: "white", borderColor: "rgba(255, 255, 255, 0.5)" },
          }}
          sx={{
            "& .MuiOutlinedInput-root": {
              "& fieldset": {
                borderColor: "rgba(255, 255, 255, 0.5)",
              },
              "&:hover fieldset": {
                borderColor: "#7f5af0",
              },
              "&.Mui-focused fieldset": {
                borderColor: "#7f5af0",
              },
            },
          }}
        />
        <Button
          fullWidth
          variant="contained"
          sx={{
            backgroundColor: "linear-gradient(to right, #7f5af0, #2d89ef)",
            "&:hover": {
              backgroundColor: "rgba(127, 90, 240, 0.9)",
            },
          }}
        >
          Send Message
        </Button>
      </form>
    </div>
  </section>
);

export default ContactForm;
